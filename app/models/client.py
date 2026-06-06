from datetime import datetime
from uuid import UUID, uuid4
from sqlalchemy import String, Integer, DateTime, ForeignKey, Text, func
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Client(Base):
    __tablename__ = "clients"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False)
    phone: Mapped[str | None] = mapped_column(String, nullable=True)
    company_name: Mapped[str | None] = mapped_column(String, nullable=True)
    industry: Mapped[str | None] = mapped_column(String, nullable=True)
    status: Mapped[str] = mapped_column(String, default="prospect")  # active, inactive, prospect
    health_score: Mapped[int] = mapped_column(Integer, default=100)  # 0-100, auto-calculated
    last_contact_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    tags: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    source: Mapped[str] = mapped_column(String, default="other")  # referral, website, cold_outreach, existing, other
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="clients")
    projects: Mapped[list["Project"]] = relationship("Project", back_populates="client", cascade="all, delete-orphan")
    activities: Mapped[list["Activity"]] = relationship("Activity", back_populates="client", cascade="all, delete-orphan")
    proposals: Mapped[list["Proposal"]] = relationship("Proposal", back_populates="client", cascade="all, delete-orphan")
    email_drafts: Mapped[list["EmailDraft"]] = relationship("EmailDraft", back_populates="client", cascade="all, delete-orphan")
