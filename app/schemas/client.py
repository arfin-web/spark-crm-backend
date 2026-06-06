from datetime import datetime
from uuid import UUID
from typing import Literal
from pydantic import BaseModel, EmailStr


class ClientBase(BaseModel):
    name: str
    email: EmailStr
    phone: str | None = None
    company_name: str | None = None
    industry: str | None = None
    status: Literal["active", "inactive", "prospect"] = "prospect"
    tags: list[str] | None = None
    notes: str | None = None
    source: Literal["referral", "website", "cold_outreach", "existing", "other"] = "other"


class ClientCreate(ClientBase):
    pass


class ClientUpdate(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    company_name: str | None = None
    industry: str | None = None
    status: Literal["active", "inactive", "prospect"] | None = None
    tags: list[str] | None = None
    notes: str | None = None
    source: Literal["referral", "website", "cold_outreach", "existing", "other"] | None = None


class ClientOut(ClientBase):
    id: UUID
    user_id: UUID
    health_score: int
    last_contact_date: datetime | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ClientAISummaryOut(BaseModel):
    summary: str
    recommendations: str


class ClientHealthScoreOut(BaseModel):
    health_score: int
    explanation: str
