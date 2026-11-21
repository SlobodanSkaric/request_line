import uuid
from enum import StrEnum

from sqlalchemy import Enum, String, Uuid, true
from sqlalchemy.orm import  Mapped, mapped_column

from app.db.base import Base
from app.db.mixins import TimestampsMixins

class UserRoles(StrEnum):
    ADMIN = 'admin'
    USER = 'user'
    APPROVER = 'approver'

class Users(TimestampsMixins, Base):
    __tablename__ = 'users'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(320), unique=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRoles] = mapped_column(
        Enum(UserRoles, native_enum=False, length=20, values_callable=lambda e: [m.value for m in e]),
        default=UserRoles.USER,
        server_default=UserRoles.USER.value,
    )
    is_active: Mapped[bool] = mapped_column(default=True, server_default=true())

