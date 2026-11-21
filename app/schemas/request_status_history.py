import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.requests import  RequestStatus

class RequestStatusHistoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    request_id: uuid.UUID
    from_status: RequestStatus | None
    to_status: RequestStatus
    changed_by_id: uuid.UUID | None
    source: str
    reason: str | None
    created_at: datetime