from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Index, Integer, PrimaryKeyConstraint, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import JSON

from app.core.database import Base


class MessageArchive(Base):
    """冷区归档表：存储超过 MESSAGE_ARCHIVE_AFTER_DAYS 天的消息记录。

    复合主键 (id, created_at) 是 MySQL RANGE COLUMNS 分区的硬性要求。
    无 FK 约束：归档时用户/会话可能已软删除，不应依赖主表引用完整性。
    """

    __tablename__ = "messages_archive"

    id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    conversation_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    images: Mapped[list | None] = mapped_column(JSON, nullable=True)
    docs: Mapped[list | None] = mapped_column(JSON, nullable=True)
    input_tokens: Mapped[int] = mapped_column(Integer, default=0)
    output_tokens: Mapped[int] = mapped_column(Integer, default=0)
    feishu_synced: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint("id", "created_at"),
        Index("idx_arch_msg_conv", "conversation_id"),
        Index("idx_arch_msg_user_date", "user_id", "created_at"),
    )
