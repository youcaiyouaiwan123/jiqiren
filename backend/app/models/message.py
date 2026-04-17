from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Enum, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import JSON

from app.core.database import Base


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    conversation_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("conversations.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)
    role: Mapped[str] = mapped_column(Enum("user", "assistant", name="msg_role_enum"), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    images: Mapped[list | None] = mapped_column(JSON, nullable=True)
    docs: Mapped[list | None] = mapped_column(JSON, nullable=True)
    input_tokens: Mapped[int] = mapped_column(Integer, default=0)
    output_tokens: Mapped[int] = mapped_column(Integer, default=0)
    feishu_synced: Mapped[int] = mapped_column(Integer, default=0)
    feishu_record_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    __table_args__ = (
        Index("idx_msg_conv", "conversation_id"),
        Index("idx_msg_user", "user_id"),
        Index("idx_msg_sync", "feishu_synced"),
        Index("idx_msg_conv_created_id", "conversation_id", "created_at", "id"),
        Index("idx_msg_created_user", "created_at", "user_id"),
        Index("idx_msg_role_created", "role", "created_at"),
    )
