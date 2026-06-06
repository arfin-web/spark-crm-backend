from datetime import datetime
from uuid import UUID
from pydantic import BaseModel


class AIInteractionOut(BaseModel):
    id: UUID
    user_id: UUID
    feature_type: str
    input_tokens: int
    output_tokens: int
    created_at: datetime

    class Config:
        from_attributes = True


class AIStatsOut(BaseModel):
    total_interactions: int
    total_input_tokens: int
    total_output_tokens: int
    interactions_by_type: dict[str, int]
    tokens_by_type: dict[str, int]
