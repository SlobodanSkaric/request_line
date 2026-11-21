import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field,ConfigDict, field_validator, model_validator

from app.models.requests import RequestStatus

class RequestCreate(BaseModel):
    request_type_id: uuid.UUID
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1)
    amount: Decimal | None = Field(default=None, max_digits=12, decimal_places=2, gt=0)
    currency: str | None = Field(default=None, min_length=3, max_length=3)
    idempotency_key: str | None = Field(default=None, min_length=1, max_length=64)

    @field_validator("title", "description")
    @classmethod
    def strip_text(cls, value: str) -> str:
        cleaned_value = value.strip()
        if not cleaned_value:
            raise ValueError("Title or description cannot be empty")
        return cleaned_value

    @field_validator("currency")
    @classmethod
    def normalize_currency(cls, value: str) -> str:
        if value is None:
            return None
        return value.upper()

    @model_validator(mode="after")
    def amount_and_currency_together(self) -> "RequestCreate":
        if (self.amount is None) != (self.currency is None):
            raise ValueError("amount and currency must both be set or both be null")
        return self


class RequestRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    requester_id: uuid.UUID
    request_type_id: uuid.UUID
    title: str
    description: str
    amount: Decimal | None
    currency: str | None
    status: RequestStatus
    decided_by_id: uuid.UUID | None
    decided_at: datetime | None
    decision_reason: str | None
    version: int
    created_at: datetime
    updated_at: datetime

class RequestDecision(BaseModel):
    decision: RequestStatus
    reason: str | None = Field(default=None, max_length=2000)

    @field_validator("decision")
    @classmethod
    def only_final_decisions(cls, value: RequestStatus) -> RequestStatus:
        if value not in {RequestStatus.APPROVED, RequestStatus.REJECTED}:
            raise ValueError("decision must be approved or rejected")
        return value

    @field_validator("reason")
    @classmethod
    def strip_reason(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned or None
