from datetime import datetime
from decimal import Decimal
from uuid import UUID
from typing import Literal
from pydantic import BaseModel


class ProposalBase(BaseModel):
    title: str
    brief_description: str
    scope: str
    deliverables: str
    timeline: str
    cost: Decimal | None = None
    status: Literal["draft", "sent", "accepted", "rejected"] = "draft"


class ProposalCreate(ProposalBase):
    client_id: UUID
    project_id: UUID | None = None


class ProposalUpdate(BaseModel):
    title: str | None = None
    brief_description: str | None = None
    scope: str | None = None
    deliverables: str | None = None
    timeline: str | None = None
    cost: Decimal | None = None
    status: Literal["draft", "sent", "accepted", "rejected"] | None = None


class ProposalGenerateRequest(BaseModel):
    client_id: UUID
    project_id: UUID | None = None
    title: str
    brief_description: str


class ProposalOut(ProposalBase):
    id: UUID
    user_id: UUID
    client_id: UUID
    project_id: UUID | None = None
    ai_generated: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
