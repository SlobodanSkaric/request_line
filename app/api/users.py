from fastapi import APIRouter, status

from app.api.deps import SessionDep
from app.schemas.users import UserCreate,UserRead
from app.services.users import register_user

router = APIRouter(prefix="/users", tags=["users"])

@router.post("", response_model=UserRead ,status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate,  db: SessionDep) -> UserRead:
    user = await register_user(db, user)
    return UserRead.model_validate(user)
