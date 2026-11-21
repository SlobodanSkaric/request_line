import uuid
from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import (
CheckConstraint,
DateTime,
Enum,
ForeignKey,
Index,
Numeric,
String,
Text,
UniqueConstraint,
Uuid,
text
)

from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from app.db.mixins import TimestampsMixins


if TYPE_CHECKING:
    from app.models.request_types import RequestTypes
    from app.models.users import Users


class RequestStatus(StrEnum):
    RECEIVED = "received"
    PROCESSING = "processing"
    NEEDS_REVIEW = "needs_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"

class Requests(TimestampsMixins, Base):
    __tablename__ = "requests"
    __table_args__ = (
        UniqueConstraint(
            "requester_id",
            "idempotency_key",
            name="uq_requests_requester_id_idempotency_key"
        ),
        CheckConstraint("length(trim(title)) > 0", name="title_not_blank"),
        CheckConstraint("amount IS NULL OR amount > 0", name="amount_positive"),
        CheckConstraint("currency IS NULL OR currency ~ '^[A-Z]{3}$'", name="currency_format"),
        CheckConstraint("(currency IS NULL) = (amount IS NULL)", name="amount_currency_together"),
        CheckConstraint("status NOT IN ('approved', 'rejected') OR decided_at IS NOT NULL", name="decision_has_timestamp"),
        Index("ix_requests_requester_id_created_at",  "requester_id", "created_at"),
        Index("ix_requests_status_created_at", "status", "created_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    requester_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"))
    request_type_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("request_types.id", ondelete="RESTRICT"))
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text)
    amount: Mapped[Decimal | None] = mapped_column(Numeric(12,2))
    currency: Mapped[str | None] = mapped_column(String(3))
    status: Mapped[RequestStatus] = mapped_column(Enum(
        RequestStatus,
        native_enum=False,
        length=20,
        values_callable=lambda e: [m.value for m in e],
    ),
        default=RequestStatus.RECEIVED,
        server_default=RequestStatus.RECEIVED.value,
    )
    decided_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    decided_by_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"))
    decision_reason: Mapped[str | None] = mapped_column(Text)
    idempotency_key: Mapped[str | None] = mapped_column(String(64))
    version: Mapped[int] = mapped_column(server_default=text("1"))

    requester: Mapped["Users"] = relationship(foreign_keys=[requester_id], lazy="raise")
    request_type: Mapped["RequestTypes"] = relationship(foreign_keys=[request_type_id], lazy="raise")
    decided_by: Mapped["Users | None"] = relationship(foreign_keys=[decided_by_id], lazy="raise")

    __mapper_args__ = {"version_id_col": version}


