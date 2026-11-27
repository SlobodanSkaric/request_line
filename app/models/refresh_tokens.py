import uuid
from datetime import datetime
from typing import TYPE_CHECKING


from sqlalchemy import  DateTime,ForeignKey,Uuid,Index,func,String
from sqlalchemy.orm import Mapped,mapped_column,relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.users import Users

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    __table_args__ = (
        Index("ix_refresh_tokens_user_id_revoked_at", "user_id", "revoked_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    token_hash: Mapped[str] = mapped_column(String(64), unique=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    replaced_by_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("refresh_tokens.id", ondelete="SET NULL")
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["Users"] = relationship(lazy="raise")
    replaced_by: Mapped["RefreshToken | None"] = relationship(lazy="raise", remote_side=[id], foreign_keys=[replaced_by_id])
