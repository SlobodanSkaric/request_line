import uuid
from decimal import Decimal

from sqlalchemy import CheckConstraint, Numeric, String, Text, Uuid, false, true
from sqlalchemy.orm import Mapped,mapped_column

from app.db.base import Base
from app.db.mixins import TimestampsMixins

class RequestTypes(TimestampsMixins, Base):
    __tablename__ = 'request_types'
    __table_args__ = (
        CheckConstraint(
            "code ~ '^[a-z][a-z0-9_]*$'", name="code_format"
        ),
        CheckConstraint(
            "approval_threshold IS NULL OR approval_threshold >= 0",
            name="approval_threshold_non_negative",
        ),
        CheckConstraint(
            "approval_threshold IS NULL OR requires_amount=True",
            name="threshold_requires_amount",
        )
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    code: Mapped[str] = mapped_column(String(50), unique=True)
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str | None] = mapped_column(Text)
    requires_amount: Mapped[bool] = mapped_column(default=False, server_default=false())
    approval_threshold: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    is_active: Mapped[bool] = mapped_column(default=True, server_default=true())