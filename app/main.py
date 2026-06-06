from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings  # noqa: F401 — validates env vars at startup
from app.core.database import Base, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Runs startup code before the app accepts requests,
    and cleanup code when the app shuts down.
    This replaces the old @app.on_event("startup") style.
    """
    # STARTUP: Create all tables in the database if they don't exist yet
    # In production, you'd use Alembic migrations instead
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield  # App is running — handling requests

    # SHUTDOWN: Clean up database connections
    await engine.dispose()


# Create the FastAPI app instance
app = FastAPI(
    title="Spark-CRM Backend API",
    description="An AI-Powered CRM backend for digital agencies with client health scoring, proposal generators, and email drafting.",
    version="1.0.0",
    lifespan=lifespan,
)


# CORS Middleware — allows your Next.js frontend to call this API.
# Without this, browsers block cross-origin requests for security.
# In production, replace "*" with your actual frontend URL.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://your-production-domain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


from app.api.v1 import v1_router
app.include_router(v1_router, prefix="/api/v1")


@app.get("/", tags=["health"])
async def health_check():
    """Simple health check endpoint. Useful for deployment platforms."""
    return {"status": "ok", "message": "API is running"}