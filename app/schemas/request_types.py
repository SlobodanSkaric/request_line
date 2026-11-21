import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

class RequestTypeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    code: str
    name: str
    description: str | None
    requires_amount: bool
    approval_threshold: Decimal | None = Field(max_digits=12, decimal_places=2)
    is_active: bool
    created_at: datetime
    updated_at: datetime
