import uuid
from encodings import aliases
from uuid import UUID
from typing import Annotated

from fastapi import Depends, HTTPException, Header ,status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.models.users import Users
from app.services.exceptions import NotFoundError
from app.services.users import get_user_by_id

SessionDep = Annotated[AsyncSession, Depends(get_session)]

