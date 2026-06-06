from datetime import datetime
from uuid import UUID, uuid4
from sqlalchemy import String, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Activity(Base):
    __tablename__ = "activities"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    client_id: Mapped[UUID | None] = mapped_column(ForeignKey("clients.id", ondelete="SET NULL"), nullable=True)
    project_id: Mapped[UUID | None] = mapped_column(ForeignKey("projects.id", ondelete="SET NULL"), nullable=True)
    type: Mapped[str] = mapped_column(String, nullable=False)  # email, call, meeting, proposal, note
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="activities")
    client: Mapped["Client"] = relationship("Client", back_populates="activities")
    project: Mapped["Project"] = relationship("Project", back_populates="activities")
