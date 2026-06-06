from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings


# create_async_engine: Creates the async connection to Neon PostgreSQL.
# pool_pre_ping=True: Tests each connection before using it (avoids "connection closed" errors)
engine = create_async_engine(
    settings.DATABASE_URL,
    connect_args={"ssl": "require"},
    pool_pre_ping=True,
    echo=False,  # Set True to log all SQL queries (useful for debugging)
)

# Session factory. Each HTTP request gets its own session (database conversation).
# expire_on_commit=False: Keep data accessible after a commit (important for async)
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """All SQLAlchemy models inherit from this Base class."""
    pass


async def get_db() -> AsyncSession:
    """
    Dependency injected into every route that needs DB access.
    'async with' ensures the session is always closed after the request,
    even if an error occurs.
    """
    async with AsyncSessionLocal() as session:
        yield session