from datetime import datetime
from uuid import UUID, uuid4
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class EmailDraft(Base):
    __tablename__ = "email_drafts"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    client_id: Mapped[UUID | None] = mapped_column(ForeignKey("clients.id", ondelete="SET NULL"), nullable=True)
    subject: Mapped[str] = mapped_column(String, nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    purpose: Mapped[str] = mapped_column(String, default="custom")  # follow_up, proposal, check_in, custom
    status: Mapped[str] = mapped_column(String, default="draft")  # draft, sent
    ai_generated: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="email_drafts")
    client: Mapped["Client"] = relationship("Client", back_populates="email_drafts")
