from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api import deps
from app.core.database import get_db
from app.models.user import User
from app.models.client import Client
from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectOut

router = APIRouter()


@router.get("/", response_model=list[ProjectOut])
async def list_projects(
    client_id: str | None = None,
    status_filter: str | None = Query(None, alias="status"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """List all projects for the authenticated user, optionally filtering by client or status."""
    query = select(Project).where(Project.user_id == current_user.id)
    
    if client_id:
        query = query.where(Project.client_id == client_id)
        
    if status_filter:
        query = query.where(Project.status == status_filter)
        
    query = query.order_by(Project.created_at.desc())
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/", response_model=ProjectOut, status_code=status.HTTP_201_CREATED)
async def create_project(
    data: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """Create a new project for an existing client."""
    # Verify client exists and belongs to current user
    client_result = await db.execute(
        select(Client).where(Client.id == data.client_id, Client.user_id == current_user.id)
    )
    client = client_result.scalars().first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found.")
        
    project = Project(
        user_id=current_user.id,
        client_id=data.client_id,
        name=data.name,
        description=data.description,
        status=data.status,
        budget=data.budget,
        estimated_hours=data.estimated_hours,
        start_date=data.start_date,
        end_date=data.end_date
    )
    db.add(project)
    await db.commit()
    await db.refresh(project)
    return project


@router.get("/{project_id}", response_model=ProjectOut)
async def get_project(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """Get project details by ID."""
    result = await db.execute(
        select(Project).where(Project.id == project_id, Project.user_id == current_user.id)
    )
    project = result.scalars().first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")
    return project


@router.put("/{project_id}", response_model=ProjectOut)
async def update_project(
    project_id: str,
    data: ProjectUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """Update details of a project."""
    result = await db.execute(
        select(Project).where(Project.id == project_id, Project.user_id == current_user.id)
    )
    project = result.scalars().first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")
        
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(project, field, value)
        
    await db.commit()
    await db.refresh(project)
    return project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """Delete a project."""
    result = await db.execute(
        select(Project).where(Project.id == project_id, Project.user_id == current_user.id)
    )
    project = result.scalars().first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")
        
    await db.delete(project)
    await db.commit()
    return
