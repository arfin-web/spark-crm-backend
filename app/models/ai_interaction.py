from datetime import datetime
from uuid import UUID, uuid4
from sqlalchemy import String, Integer, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class AIInteraction(Base):
    __tablename__ = "ai_interactions"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    feature_type: Mapped[str] = mapped_column(String, nullable=False)  # email_draft, proposal, summary, scoring
    input_tokens: Mapped[int] = mapped_column(Integer, default=0)
    output_tokens: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="ai_interactions")
