from datetime import date, datetime
from decimal import Decimal
from uuid import UUID
from typing import Literal
from pydantic import BaseModel


class ProjectBase(BaseModel):
    name: str
    description: str | None = None
    status: Literal["prospect", "proposal_sent", "in_progress", "completed", "paused"] = "prospect"
    budget: Decimal | None = None
    estimated_hours: int | None = None
    start_date: date | None = None
    end_date: date | None = None


class ProjectCreate(ProjectBase):
    client_id: UUID


class ProjectUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    status: Literal["prospect", "proposal_sent", "in_progress", "completed", "paused"] | None = None
    budget: Decimal | None = None
    estimated_hours: int | None = None
    start_date: date | None = None
    end_date: date | None = None


class ProjectOut(ProjectBase):
    id: UUID
    user_id: UUID
    client_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
