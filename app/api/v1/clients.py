from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api import deps
from app.core.database import get_db
from app.core.ai import ai_client
from app.models.user import User
from app.models.client import Client
from app.models.activity import Activity
from app.models.ai_interaction import AIInteraction
from app.schemas.client import ClientCreate, ClientUpdate, ClientOut, ClientAISummaryOut, ClientHealthScoreOut

router = APIRouter()


@router.get("/", response_model=list[ClientOut])
async def list_clients(
    status_filter: str | None = Query(None, alias="status"),
    search: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """Retrieve all clients for the authenticated user, supporting filters and search."""
    query = select(Client).where(Client.user_id == current_user.id)
    
    if status_filter:
        query = query.where(Client.status == status_filter)
    
    if search:
        query = query.where(
            Client.name.ilike(f"%{search}%") | 
            Client.email.ilike(f"%{search}%") | 
            (Client.company_name.ilike(f"%{search}%") if Client.company_name is not None else False)
        )
        
    query = query.order_by(Client.name)
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/", response_model=ClientOut, status_code=status.HTTP_201_CREATED)
async def create_client(
    data: ClientCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """Create a new client for the agency."""
    client = Client(
        user_id=current_user.id,
        name=data.name,
        email=data.email,
        phone=data.phone,
        company_name=data.company_name,
        industry=data.industry,
        status=data.status,
        tags=data.tags or [],
        notes=data.notes,
        source=data.source,
        health_score=100  # Default initial health score
    )
    db.add(client)
    await db.commit()
    await db.refresh(client)
    return client


@router.get("/{client_id}", response_model=ClientOut)
async def get_client(
    client_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """Get details for a specific client."""
    result = await db.execute(
        select(Client).where(Client.id == client_id, Client.user_id == current_user.id)
    )
    client = result.scalars().first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found.")
    return client


@router.put("/{client_id}", response_model=ClientOut)
async def update_client(
    client_id: str,
    data: ClientUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """Update details of a specific client."""
    result = await db.execute(
        select(Client).where(Client.id == client_id, Client.user_id == current_user.id)
    )
    client = result.scalars().first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found.")
        
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(client, field, value)
        
    await db.commit()
    await db.refresh(client)
    return client


@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_client(
    client_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """Delete a specific client."""
    result = await db.execute(
        select(Client).where(Client.id == client_id, Client.user_id == current_user.id)
    )
    client = result.scalars().first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found.")
        
    await db.delete(client)
    await db.commit()
    return


@router.post("/{client_id}/score-health", response_model=ClientHealthScoreOut)
async def score_client_health(
    client_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """Triggers an AI assessment to score the relationship health of a client based on activities."""
    # 1. Fetch client
    result = await db.execute(
        select(Client).where(Client.id == client_id, Client.user_id == current_user.id)
    )
    client = result.scalars().first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found.")
        
    # 2. Fetch recent activities
    act_result = await db.execute(
        select(Activity).where(Activity.client_id == client.id).order_by(Activity.created_at.desc()).limit(15)
    )
    activities = act_result.scalars().all()
    
    # 3. Create a quick text summary of activities
    activities_summary = ""
    for act in activities:
        activities_summary += f"- [{act.created_at.strftime('%Y-%m-%d')}] {act.type.upper()}: {act.title} - {act.description[:100]}\n"
        
    # 4. Trigger AI Health Scoring
    ai_res = await ai_client.calculate_client_health(
        client_name=client.name,
        client_notes=client.notes,
        activities_summary=activities_summary
    )
    
    score = ai_res.get("health_score", 100)
    explanation = ai_res.get("explanation", "Assessment completed.")
    
    # 5. Log AI Interaction
    interaction = AIInteraction(
        user_id=current_user.id,
        feature_type="scoring",
        input_tokens=ai_res.get("input_tokens", 0),
        output_tokens=ai_res.get("output_tokens", 0)
    )
    db.add(interaction)
    
    # 6. Update client health score
    client.health_score = score
    await db.commit()
    await db.refresh(client)
    
    return {"health_score": score, "explanation": explanation}


@router.get("/{client_id}/ai-summary", response_model=ClientAISummaryOut)
async def get_client_summary(
    client_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """Generates an AI summary and recommendations report for a client based on history."""
    # 1. Fetch client
    result = await db.execute(
        select(Client).where(Client.id == client_id, Client.user_id == current_user.id)
    )
    client = result.scalars().first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found.")
        
    # 2. Fetch client activities
    act_result = await db.execute(
        select(Activity).where(Activity.client_id == client.id).order_by(Activity.created_at.desc()).limit(20)
    )
    activities = act_result.scalars().all()
    
    # 3. Text summary of activities
    activities_summary = ""
    for act in activities:
        activities_summary += f"- {act.created_at.strftime('%Y-%m-%d')} ({act.type.upper()}): {act.title} - {act.description[:100]}\n"
        
    # 4. Trigger AI call
    ai_res = await ai_client.generate_client_summary(
        client_name=client.name,
        client_industry=client.industry,
        activities_summary=activities_summary,
        client_notes=client.notes
    )
    
    # 5. Log AI Interaction
    interaction = AIInteraction(
        user_id=current_user.id,
        feature_type="summary",
        input_tokens=ai_res.get("input_tokens", 0),
        output_tokens=ai_res.get("output_tokens", 0)
    )
    db.add(interaction)
    await db.commit()
    
    return {
        "summary": ai_res.get("summary", "Client summary generated."),
        "recommendations": ai_res.get("recommendations", "Establish further contact.")
    }
