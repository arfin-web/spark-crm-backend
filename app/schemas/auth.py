from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, EmailStr


class UserRegister(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    agency_name: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class UserOut(BaseModel):
    id: UUID
    email: EmailStr
    first_name: str
    last_name: str
    agency_name: str
    subscription_tier: str
    subscription_status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
