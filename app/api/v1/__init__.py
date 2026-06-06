from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.clients import router as clients_router
from app.api.v1.projects import router as projects_router
from app.api.v1.activities import router as activities_router
from app.api.v1.proposals import router as proposals_router
from app.api.v1.email_drafts import router as email_drafts_router
from app.api.v1.ai import router as ai_router

v1_router = APIRouter()

v1_router.include_router(auth_router, prefix="/auth", tags=["auth"])
v1_router.include_router(clients_router, prefix="/clients", tags=["clients"])
v1_router.include_router(projects_router, prefix="/projects", tags=["projects"])
v1_router.include_router(activities_router, prefix="/activities", tags=["activities"])
v1_router.include_router(proposals_router, prefix="/proposals", tags=["proposals"])
v1_router.include_router(email_drafts_router, prefix="/email-drafts", tags=["email-drafts"])
v1_router.include_router(ai_router, prefix="/ai", tags=["ai"])
