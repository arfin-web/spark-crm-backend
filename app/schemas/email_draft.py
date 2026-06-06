from datetime import datetime
from uuid import UUID
from typing import Literal
from pydantic import BaseModel


class EmailDraftBase(BaseModel):
    subject: str
    body: str
    purpose: Literal["follow_up", "proposal", "check_in", "custom"] = "custom"
    status: Literal["draft", "sent"] = "draft"


class EmailDraftCreate(EmailDraftBase):
    client_id: UUID | None = None


class EmailDraftUpdate(BaseModel):
    subject: str | None = None
    body: str | None = None
    purpose: Literal["follow_up", "proposal", "check_in", "custom"] | None = None
    status: Literal["draft", "sent"] | None = None


class EmailDraftGenerateRequest(BaseModel):
    client_id: UUID | None = None
    purpose: Literal["follow_up", "proposal", "check_in", "custom"]
    notes: str | None = None


class EmailDraftOut(EmailDraftBase):
    id: UUID
    user_id: UUID
    client_id: UUID | None = None
    ai_generated: bool
    created_at: datetime

    class Config:
        from_attributes = True
