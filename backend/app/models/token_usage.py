from datetime import datetime

from sqlalchemy import BigInteger, DateTime, DECIMAL, ForeignKey, Index, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class TokenUsage(Base):
    __tablename__ = "token_usage"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=True)
    message_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    model: Mapped[str | None] = mapped_column(String(50))
    input_tokens: Mapped[int] = mapped_column(Integer, nullable=False)
    output_tokens: Mapped[int] = mapped_column(Integer, nullable=False)
    cache_read_tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=0, comment="缓存命中读取 token 数")
    cache_creation_tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=0, comment="缓存写入 token 数")
    cost_usd: Mapped[float | None] = mapped_column(DECIMAL(10, 6), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    __table_args__ = (
        Index("idx_tu_user", "user_id"),
        Index("idx_tu_date", "created_at"),
        Index("idx_tu_date_model", "created_at", "model"),
        Index("idx_tu_message", "message_id"),
    )
