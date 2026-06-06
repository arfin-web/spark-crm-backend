from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api import deps
from app.core.database import get_db
from app.models.user import User
from app.models.client import Client
from app.models.project import Project
from app.models.activity import Activity
from app.schemas.activity import ActivityCreate, ActivityOut

router = APIRouter()


async def recalculate_client_health_score(db: AsyncSession, client: Client):
    """
    Recalculates client health score reactively using a rule-based algorithm:
    - Base score: 80
    - Interaction points: Email (+3), Call (+5), Meeting (+8), Proposal (+10), Note (+1)
    - Decay: -1 point per day since the last interaction
    - Sentiment adjustments based on client notes.
    - Constrained between 0 and 100.
    """
    # 1. Fetch all activities for this client
    result = await db.execute(
        select(Activity).where(Activity.client_id == client.id).order_by(Activity.created_at.desc())
    )
    activities = result.scalars().all()
    
    if not activities:
        # Decent initial default if no activities
        score = 80
        if client.notes:
            notes_lower = client.notes.lower()
            if any(w in notes_lower for w in ["unhappy", "delay", "issue", "frustrated"]):
                score -= 20
        client.health_score = max(min(score, 100), 0)
        return
        
    score = 80
    # Add points for interaction density
    for act in activities[:10]:  # Look at the 10 most recent interactions
        if act.type == "call":
            score += 5
        elif act.type == "meeting":
            score += 8
        elif act.type == "email":
            score += 3
        elif act.type == "proposal":
            score += 10
        elif act.type == "note":
            score += 1
            
    # Subtact points for decay (days since last contact)
    last_act = activities[0]
    days_since = (datetime.utcnow() - last_act.created_at).days
    score -= min(days_since * 1.5, 40)  # Max decay of 40 points
    
    # Analyze notes sentiment
    if client.notes:
        notes_lower = client.notes.lower()
        if any(w in notes_lower for w in ["happy", "thrilled", "great", "excellent", "pleased"]):
            score += 10
        if any(w in notes_lower for w in ["unhappy", "delay", "issue", "frustrated", "bug", "broken"]):
            score -= 25
            
    # Bound health score between 0 and 100
    client.health_score = int(max(min(score, 100), 0))


@router.get("/", response_model=list[ActivityOut])
async def list_activities(
    client_id: str | None = None,
    project_id: str | None = None,
    activity_type: str | None = Query(None, alias="type"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """List all activities for the current user, optionally filtering by client, project, or type."""
    query = select(Activity).where(Activity.user_id == current_user.id)
    
    if client_id:
        query = query.where(Activity.client_id == client_id)
        
    if project_id:
        query = query.where(Activity.project_id == project_id)
        
    if activity_type:
        query = query.where(Activity.type == activity_type)
        
    query = query.order_by(Activity.created_at.desc())
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/", response_model=ActivityOut, status_code=status.HTTP_201_CREATED)
async def create_activity(
    data: ActivityCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """Log a new activity. Triggers last_contact_date updates and health score recalculation."""
    client = None
    if data.client_id:
        # Check client ownership
        client_res = await db.execute(
            select(Client).where(Client.id == data.client_id, Client.user_id == current_user.id)
        )
        client = client_res.scalars().first()
        if not client:
            raise HTTPException(status_code=404, detail="Client not found.")
            
    if data.project_id:
        # Check project ownership
        project_res = await db.execute(
            select(Project).where(Project.id == data.project_id, Project.user_id == current_user.id)
        )
        project = project_res.scalars().first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found.")
            
    # Create the activity
    activity = Activity(
        user_id=current_user.id,
        client_id=data.client_id,
        project_id=data.project_id,
        type=data.type,
        title=data.title,
        description=data.description,
        created_at=datetime.utcnow()
    )
    db.add(activity)
    
    # Side effects if a client is associated
    if client:
        # 1. Update last contact date if it is an active interaction type
        if data.type in ["email", "call", "meeting"]:
            client.last_contact_date = activity.created_at
            
        # 2. Re-calculate client health score reactively
        # Needs to flush or commit activity first to include it in the query
        await db.flush()
        await recalculate_client_health_score(db, client)
        
    await db.commit()
    await db.refresh(activity)
    return activity


@router.get("/{activity_id}", response_model=ActivityOut)
async def get_activity(
    activity_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """Get detail of a logged activity by ID."""
    result = await db.execute(
        select(Activity).where(Activity.id == activity_id, Activity.user_id == current_user.id)
    )
    activity = result.scalars().first()
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found.")
    return activity


@router.delete("/{activity_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_activity(
    activity_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """Delete an activity. Triggers a health score update if a client is attached."""
    result = await db.execute(
        select(Activity).where(Activity.id == activity_id, Activity.user_id == current_user.id)
    )
    activity = result.scalars().first()
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found.")
        
    client_id = activity.client_id
    await db.delete(activity)
    await db.flush()
    
    # Recalculate client health score if client was attached
    if client_id:
        client_res = await db.execute(
            select(Client).where(Client.id == client_id, Client.user_id == current_user.id)
        )
        client = client_res.scalars().first()
        if client:
            await recalculate_client_health_score(db, client)
            
    await db.commit()
    return
