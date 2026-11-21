import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, ConfigDict, Field, field_validator

from app.models.users import UserRoles

class UserCreate(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=1, max_length=255)
    password: str = Field(min_length=8, max_length=128)

    @field_validator('email')
    @classmethod
    def normalize_email(cls, value: str) -> EmailStr:
        return value.lower()

    @field_validator('full_name')
    @classmethod
    def strip_name(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError('Users must have a full name, and no spaces.')
        return cleaned

class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: EmailStr
    full_name: str
    role: UserRoles
    is_active: bool
    created_at: datetime
    updated_at: datetime