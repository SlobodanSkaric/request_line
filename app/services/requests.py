import uuid
from datetime import UTC, datetime
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models.request_status_history import RequestStatusHistory
from app.models.request_types import RequestTypes
from app.models.requests import RequestStatus, Requests
from app.models.users import UserRoles, Users
from app.schemas.requests import RequestCreate, RequestDecision
from app.services.exceptions import (
    ConflictError,
    ForbiddenError,
    NotFoundError,
    ValidationError,
)
ALLOWED_TRANSITIONS: dict[RequestStatus, set[RequestStatus]] = {
    RequestStatus.RECEIVED: {RequestStatus.PROCESSING, RequestStatus.CANCELLED},
    RequestStatus.PROCESSING: {
        RequestStatus.NEEDS_REVIEW,
        RequestStatus.APPROVED,
        RequestStatus.REJECTED,
    },
    RequestStatus.NEEDS_REVIEW: {
        RequestStatus.PROCESSING,
        RequestStatus.APPROVED,
        RequestStatus.REJECTED,
    },
    RequestStatus.APPROVED: set(),
    RequestStatus.REJECTED: set(),
    RequestStatus.CANCELLED: set(),
}
async def create_request(session: AsyncSession, *, requester: Users, data: RequestCreate) -> Requests:
    request_type = await session.get(RequestTypes, data.request_type_id)
    if request_type is None or not request_type.is_active:
        raise  NotFoundError("request_type", data.request_type_id)
    if request_type.requires_amount and data.amount is None:
        raise ValidationError(
            f"Request type '{request_type.code}' requires amount and currency"
        )

    request = Requests(
        requester_id=requester.id,
        request_type_id=request_type.id,
        title=data.title,
        description=data.description,
        amount=data.amount,
        currency=data.currency,
        idempotency_key=data.idempotency_key,
        status=RequestStatus.RECEIVED,
    )
    session.add(request)
    await session.flush()

    request_history = RequestStatusHistory(
        request_id=request.id,
        from_status=None,
        to_status=RequestStatus.RECEIVED,
        changed_by_id=requester.id,
        source="api",
        reason=None,
    )

    session.add(request_history)
    await session.flush()

    try:
        await  session.commit()
    except IntegrityError as e:
        await session.rollback()
        raise  ConflictError("Duplicate idempotency key for this user") from e

    await session.refresh(request)
    return request

async def get_request(session: AsyncSession, *, request_id: uuid.UUID) -> Requests:
    result = await session.execute(
        select(Requests).where(Requests.id == request_id)
        .options(
            selectinload(Requests.requester),
            selectinload(Requests.request_type),
            selectinload(Requests.decided_by)
        )
    )

    request = result.scalar_one_or_none()
    if request is None:
        raise NotFoundError("request", request_id)
    return request

async def  change_status(session: AsyncSession, *, request_id: uuid.UUID, actor: Users, new_status: RequestStatus, source: str, reason: str | None=None) -> Requests:
    request = await get_request(session, request_id=request_id)

    old_status = request.status

    allowed = ALLOWED_TRANSITIONS[old_status]
    if new_status not in allowed:
        raise ValidationError(
            f"Cannot transition from '{old_status}' to '{new_status}'"
        )

    if new_status == RequestStatus.CANCELLED and actor.id != request.requester_id:
        raise ForbiddenError("Only the requester can cancel")

    if new_status in {RequestStatus.APPROVED, RequestStatus.REJECTED}:
        if actor.role not in {UserRoles.ADMIN, UserRoles.APPROVER}:
            raise ForbiddenError("Only approver or admin can decide")
        request.decided_by_id = actor.id
        request.decided_at = datetime.now(UTC)
        request.decision_reason = reason

    request.status = new_status
    session.add(
        RequestStatusHistory(
            request_id=request.id,
            from_status=old_status,
            to_status=new_status,
            changed_by_id=actor.id,
            source=source,
            reason=reason,
        )
    )
    await session.commit()
    await session.refresh(request)
    return request

async def decide_request(session: AsyncSession, *, request_id: uuid.UUID, actor: Users, data: RequestDecision) -> Requests:
    return await change_status(
        session,
        request_id=request_id,
        actor=actor,
        new_status=data.decision,
        source="api",
        reason=data.reason,
    )
