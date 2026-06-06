from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api import deps
from app.core.database import get_db
from app.core.ai import ai_client
from app.models.user import User
from app.models.client import Client
from app.models.activity import Activity
from app.models.email_draft import EmailDraft
from app.models.ai_interaction import AIInteraction
from app.schemas.email_draft import EmailDraftCreate, EmailDraftUpdate, EmailDraftGenerateRequest, EmailDraftOut

router = APIRouter()


@router.get("/", response_model=list[EmailDraftOut])
async def list_drafts(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """List all email drafts for the authenticated user."""
    result = await db.execute(
        select(EmailDraft).where(EmailDraft.user_id == current_user.id).order_by(EmailDraft.created_at.desc())
    )
    return result.scalars().all()


@router.post("/", response_model=EmailDraftOut, status_code=status.HTTP_201_CREATED)
async def create_draft(
    data: EmailDraftCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """Manually write an email draft."""
    if data.client_id:
        client_res = await db.execute(
            select(Client).where(Client.id == data.client_id, Client.user_id == current_user.id)
        )
        if not client_res.scalars().first():
            raise HTTPException(status_code=404, detail="Client not found.")
            
    draft = EmailDraft(
        user_id=current_user.id,
        client_id=data.client_id,
        subject=data.subject,
        body=data.body,
        purpose=data.purpose,
        status=data.status,
        ai_generated=False
    )
    db.add(draft)
    await db.commit()
    await db.refresh(draft)
    return draft


@router.post("/generate", response_model=EmailDraftOut, status_code=status.HTTP_201_CREATED)
async def generate_draft(
    data: EmailDraftGenerateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """AI-powered email draft creator: drafts context-aware emails for follow-ups, updates, and proposals."""
    client_name = "Valued Customer"
    client_industry = "Digital"
    client_notes_summary = ""
    
    if data.client_id:
        # 1. Verify and retrieve client context
        client_res = await db.execute(
            select(Client).where(Client.id == data.client_id, Client.user_id == current_user.id)
        )
        client = client_res.scalars().first()
        if not client:
            raise HTTPException(status_code=404, detail="Client not found.")
            
        client_name = client.name
        client_industry = client.industry
        
        # 2. Retrieve last few activities to build correspondence context
        act_result = await db.execute(
            select(Activity).where(Activity.client_id == client.id).order_by(Activity.created_at.desc()).limit(5)
        )
        activities = act_result.scalars().all()
        activity_strings = [
            f"{act.type.upper()}: {act.title} ({act.created_at.strftime('%Y-%m-%d')})" for act in activities
        ]
        client_notes_summary = f"Client Notes: {client.notes or 'None'}. Recent activities: {', '.join(activity_strings)}"
        
    # 3. Call AI service
    ai_res = await ai_client.generate_email_draft(
        client_name=client_name,
        client_industry=client_industry,
        purpose=data.purpose,
        notes=data.notes,
        client_notes_summary=client_notes_summary
    )
    
    # 4. Save email draft
    draft = EmailDraft(
        user_id=current_user.id,
        client_id=data.client_id,
        subject=ai_res.get("subject", "Follow up update"),
        body=ai_res.get("body", "Hi, checking in..."),
        purpose=data.purpose,
        status="draft",
        ai_generated=True
    )
    db.add(draft)
    
    # 5. Log AI Interaction
    interaction = AIInteraction(
        user_id=current_user.id,
        feature_type="email_draft",
        input_tokens=ai_res.get("input_tokens", 0),
        output_tokens=ai_res.get("output_tokens", 0)
    )
    db.add(interaction)
    
    await db.commit()
    await db.refresh(draft)
    return draft


@router.get("/{draft_id}", response_model=EmailDraftOut)
async def get_draft(
    draft_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """Get email draft details by ID."""
    result = await db.execute(
        select(EmailDraft).where(EmailDraft.id == draft_id, EmailDraft.user_id == current_user.id)
    )
    draft = result.scalars().first()
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found.")
    return draft


@router.put("/{draft_id}", response_model=EmailDraftOut)
async def update_draft(
    draft_id: str,
    data: EmailDraftUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """Update details of an email draft (such as marking as 'sent')."""
    result = await db.execute(
        select(EmailDraft).where(EmailDraft.id == draft_id, EmailDraft.user_id == current_user.id)
    )
    draft = result.scalars().first()
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found.")
        
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(draft, field, value)
        
    await db.commit()
    await db.refresh(draft)
    return draft


@router.delete("/{draft_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_draft(
    draft_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """Delete an email draft."""
    result = await db.execute(
        select(EmailDraft).where(EmailDraft.id == draft_id, EmailDraft.user_id == current_user.id)
    )
    draft = result.scalars().first()
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found.")
        
    await db.delete(draft)
    await db.commit()
    return
