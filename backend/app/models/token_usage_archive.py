from datetime import datetime

from sqlalchemy import BigInteger, DateTime, DECIMAL, Index, Integer, PrimaryKeyConstraint, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class TokenUsageArchive(Base):
    """冷区归档表：存储超过 TOKEN_USAGE_ARCHIVE_AFTER_DAYS 天的 token 计费记录。

    message_id 仅作数据溯源用，归档后不保证对应 messages 行仍存在。
    """

    __tablename__ = "token_usage_archive"

    id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    message_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    model: Mapped[str | None] = mapped_column(String(50))
    input_tokens: Mapped[int] = mapped_column(Integer, nullable=False)
    output_tokens: Mapped[int] = mapped_column(Integer, nullable=False)
    cost_usd: Mapped[float | None] = mapped_column(DECIMAL(10, 6), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint("id", "created_at"),
        Index("idx_arch_tu_user_date", "user_id", "created_at"),
        Index("idx_arch_tu_model_date", "model", "created_at"),
    )
