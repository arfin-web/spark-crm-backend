from datetime import datetime
from uuid import UUID
from typing import Literal
from pydantic import BaseModel


class ActivityBase(BaseModel):
    type: Literal["email", "call", "meeting", "proposal", "note"]
    title: str
    description: str


class ActivityCreate(ActivityBase):
    client_id: UUID | None = None
    project_id: UUID | None = None


class ActivityOut(ActivityBase):
    id: UUID
    user_id: UUID
    client_id: UUID | None = None
    project_id: UUID | None = None
    created_at: datetime

    class Config:
        from_attributes = True
