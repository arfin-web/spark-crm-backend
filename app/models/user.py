from datetime import datetime
from uuid import UUID, uuid4
from sqlalchemy import String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    first_name: Mapped[str] = mapped_column(String, nullable=False)
    last_name: Mapped[str] = mapped_column(String, nullable=False)
    agency_name: Mapped[str] = mapped_column(String, nullable=False)
    subscription_tier: Mapped[str] = mapped_column(String, default="starter")  # starter, growth, custom
    subscription_status: Mapped[str] = mapped_column(String, default="trial")  # active, inactive, trial
    password: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Relationships
    clients: Mapped[list["Client"]] = relationship("Client", back_populates="user", cascade="all, delete-orphan")
    projects: Mapped[list["Project"]] = relationship("Project", back_populates="user", cascade="all, delete-orphan")
    activities: Mapped[list["Activity"]] = relationship("Activity", back_populates="user", cascade="all, delete-orphan")
    proposals: Mapped[list["Proposal"]] = relationship("Proposal", back_populates="user", cascade="all, delete-orphan")
    email_drafts: Mapped[list["EmailDraft"]] = relationship("EmailDraft", back_populates="user", cascade="all, delete-orphan")
    ai_interactions: Mapped[list["AIInteraction"]] = relationship("AIInteraction", back_populates="user", cascade="all, delete-orphan")
