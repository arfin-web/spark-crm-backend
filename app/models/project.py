from datetime import date, datetime
from decimal import Decimal
from uuid import UUID, uuid4
from sqlalchemy import String, Integer, DateTime, Date, ForeignKey, Numeric, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    client_id: Mapped[UUID] = mapped_column(ForeignKey("clients.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String, default="prospect")  # prospect, proposal_sent, in_progress, completed, paused
    budget: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    estimated_hours: Mapped[int | None] = mapped_column(Integer, nullable=True)
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="projects")
    client: Mapped["Client"] = relationship("Client", back_populates="projects")
    activities: Mapped[list["Activity"]] = relationship("Activity", back_populates="project", cascade="all, delete-orphan")
    proposals: Mapped[list["Proposal"]] = relationship("Proposal", back_populates="project", cascade="all, delete-orphan")
