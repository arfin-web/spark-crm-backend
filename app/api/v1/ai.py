from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api import deps
from app.core.database import get_db
from app.models.user import User
from app.models.ai_interaction import AIInteraction
from app.schemas.ai_interaction import AIStatsOut

router = APIRouter()


@router.get("/stats", response_model=AIStatsOut)
async def get_ai_statistics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """Retrieve aggregate usage statistics for the user's AI integrations."""
    result = await db.execute(
        select(AIInteraction).where(AIInteraction.user_id == current_user.id)
    )
    interactions = result.scalars().all()
    
    total_interactions = len(interactions)
    total_input = 0
    total_output = 0
    
    interactions_by_type = {}
    tokens_by_type = {}
    
    for inter in interactions:
        total_input += inter.input_tokens
        total_output += inter.output_tokens
        
        ftype = inter.feature_type
        # Update interaction counts
        interactions_by_type[ftype] = interactions_by_type.get(ftype, 0) + 1
        
        # Update token totals per type
        token_sum = inter.input_tokens + inter.output_tokens
        tokens_by_type[ftype] = tokens_by_type.get(ftype, 0) + token_sum
        
    return {
        "total_interactions": total_interactions,
        "total_input_tokens": total_input,
        "total_output_tokens": total_output,
        "interactions_by_type": interactions_by_type,
        "tokens_by_type": tokens_by_type
    }
