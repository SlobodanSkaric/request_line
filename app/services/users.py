import uuid

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.models.users import Users
from app.schemas.users import UserCreate
from app.services.exceptions import ConflictError, NotFoundError

async def create_user(session: AsyncSession, user_datas: UserCreate) -> Users:
        user = Users(
            email=user_datas.email,
            full_name=user_datas.full_name,
            password_hash=hash_password(user_datas.password)
        )
        session.add(user)
        try:
            await session.commit()
        except IntegrityError as e:
            await session.rollback()
            raise ConflictError("Email already register") from e
        await  session.refresh(user)
        return user

async def get_user_by_email(session: AsyncSession, email: str) -> Users | None:
        result = await session.execute(select(Users).where(Users.email == email.lower()))
        return result.scalar_one_or_none()


async def get_user_by_id(session: AsyncSession, user_id: uuid.UUID) -> Users:
    result = await session.get(Users, user_id)
    if result is None or not result.is_active:
        raise NotFoundError("user", user_id)
    return result

