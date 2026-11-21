import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    String,
    Text,
    Uuid,
    func,
)

from  sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.requests import RequestStatus

if TYPE_CHECKING:
    from app.models.users import Users
    from app.models.requests import Requests

def _status_enum() -> Enum:
    return Enum(
        RequestStatus,
        native_enum=False,
        length=20,
        values_callable=lambda e: [m.value for m in e],
    )

class RequestStatusHistory(Base):
    __tablename__ = 'request_status_history'

    __table_args__ = (
        CheckConstraint(
            "from_status IS NULL OR from_status <> to_status",
            name="status_changed",
        ),
        CheckConstraint(
            "length(trim(source)) > 0", name="source_not_blank",
        ),
        Index("ix_request_status_history_request_id_created_at", "request_id", "created_at"),
    )
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    request_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("requests.id", ondelete="CASCADE"))
    from_status: Mapped[RequestStatus | None] = mapped_column(_status_enum())
    to_status: Mapped[RequestStatus] = mapped_column(_status_enum())
    changed_by_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"))
    source: Mapped[str] = mapped_column(String(50))
    reason: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    request: Mapped["Requests"] = relationship(lazy="raise")
    changed_by: Mapped["Users | None"] = relationship(lazy="raise")
