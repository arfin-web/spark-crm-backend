from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api import deps
from app.core.database import get_db
from app.core.ai import ai_client
from app.models.user import User
from app.models.client import Client
from app.models.project import Project
from app.models.proposal import Proposal
from app.models.ai_interaction import AIInteraction
from app.schemas.proposal import ProposalCreate, ProposalUpdate, ProposalGenerateRequest, ProposalOut

router = APIRouter()


@router.get("/", response_model=list[ProposalOut])
async def list_proposals(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """List all proposals for the authenticated user."""
    result = await db.execute(
        select(Proposal).where(Proposal.user_id == current_user.id).order_by(Proposal.created_at.desc())
    )
    return result.scalars().all()


@router.post("/", response_model=ProposalOut, status_code=status.HTTP_201_CREATED)
async def create_proposal(
    data: ProposalCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """Manually create a project proposal."""
    # Verify client ownership
    client_res = await db.execute(
        select(Client).where(Client.id == data.client_id, Client.user_id == current_user.id)
    )
    if not client_res.scalars().first():
        raise HTTPException(status_code=404, detail="Client not found.")
        
    if data.project_id:
        # Verify project ownership
        project_res = await db.execute(
            select(Project).where(Project.id == data.project_id, Project.user_id == current_user.id)
        )
        if not project_res.scalars().first():
            raise HTTPException(status_code=404, detail="Project not found.")
            
    proposal = Proposal(
        user_id=current_user.id,
        client_id=data.client_id,
        project_id=data.project_id,
        title=data.title,
        brief_description=data.brief_description,
        scope=data.scope,
        deliverables=data.deliverables,
        timeline=data.timeline,
        cost=data.cost,
        status=data.status,
        ai_generated=False
    )
    db.add(proposal)
    await db.commit()
    await db.refresh(proposal)
    return proposal


@router.post("/generate", response_model=ProposalOut, status_code=status.HTTP_201_CREATED)
async def generate_proposal(
    data: ProposalGenerateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """AI-powered proposal generator: writes project scope, deliverables, timeline, and budget estimation."""
    # 1. Verify and retrieve client
    client_res = await db.execute(
        select(Client).where(Client.id == data.client_id, Client.user_id == current_user.id)
    )
    client = client_res.scalars().first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found.")
        
    project_name = data.title
    if data.project_id:
        # Verify and retrieve project details to feed context
        project_res = await db.execute(
            select(Project).where(Project.id == data.project_id, Project.user_id == current_user.id)
        )
        project = project_res.scalars().first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found.")
        project_name = project.name
        
    # 2. Trigger AI Generation
    ai_res = await ai_client.generate_proposal(
        client_name=client.name,
        client_industry=client.industry,
        project_name=project_name,
        brief_description=data.brief_description
    )
    
    # 3. Create Proposal object
    proposal = Proposal(
        user_id=current_user.id,
        client_id=data.client_id,
        project_id=data.project_id,
        title=data.title,
        brief_description=data.brief_description,
        scope=ai_res.get("scope", "Scope details."),
        deliverables=ai_res.get("deliverables", "Deliverables details."),
        timeline=ai_res.get("timeline", "Timeline details."),
        cost=ai_res.get("cost"),
        status="draft",
        ai_generated=True
    )
    db.add(proposal)
    
    # 4. Log AI Interaction
    interaction = AIInteraction(
        user_id=current_user.id,
        feature_type="proposal",
        input_tokens=ai_res.get("input_tokens", 0),
        output_tokens=ai_res.get("output_tokens", 0)
    )
    db.add(interaction)
    
    await db.commit()
    await db.refresh(proposal)
    return proposal


@router.get("/{proposal_id}", response_model=ProposalOut)
async def get_proposal(
    proposal_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """Retrieve details of a proposal."""
    result = await db.execute(
        select(Proposal).where(Proposal.id == proposal_id, Proposal.user_id == current_user.id)
    )
    proposal = result.scalars().first()
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found.")
    return proposal


@router.put("/{proposal_id}", response_model=ProposalOut)
async def update_proposal(
    proposal_id: str,
    data: ProposalUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """Update details of a proposal."""
    result = await db.execute(
        select(Proposal).where(Proposal.id == proposal_id, Proposal.user_id == current_user.id)
    )
    proposal = result.scalars().first()
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found.")
        
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(proposal, field, value)
        
    await db.commit()
    await db.refresh(proposal)
    return proposal


@router.delete("/{proposal_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_proposal(
    proposal_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """Delete a proposal."""
    result = await db.execute(
        select(Proposal).where(Proposal.id == proposal_id, Proposal.user_id == current_user.id)
    )
    proposal = result.scalars().first()
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found.")
        
    await db.delete(proposal)
    await db.commit()
    return
