from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Index, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class MessageFeedback(Base):
    __tablename__ = "message_feedback"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    message_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("messages.id"), nullable=False, unique=True)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    conversation_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    rating: Mapped[str | None] = mapped_column(String(10), nullable=True)
    satisfaction_level: Mapped[str | None] = mapped_column(String(10), nullable=True)
    scored_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index("idx_mf_user", "user_id"),
        Index("idx_mf_conv", "conversation_id"),
    )
