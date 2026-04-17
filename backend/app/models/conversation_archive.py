from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Index, PrimaryKeyConstraint, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ConversationArchive(Base):
    """冷区归档表：存储超过 CONVERSATION_ARCHIVE_AFTER_DAYS 天的会话记录。

    归档时其下属消息已先于会话被归档（消息阈值 180 天 < 会话阈值 365 天）。
    """

    __tablename__ = "conversations_archive"

    id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    title: Mapped[str | None] = mapped_column(String(200))
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint("id", "created_at"),
        Index("idx_arch_conv_user_date", "user_id", "created_at"),
    )
