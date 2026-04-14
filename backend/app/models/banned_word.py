from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Enum, ForeignKey, Index, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class BannedWord(Base):
    __tablename__ = "banned_words"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    word: Mapped[str] = mapped_column(String(100), nullable=False)
    match_type: Mapped[str] = mapped_column(
        Enum("exact", "contains", "regex", name="match_type_enum"), default="contains"
    )
    action: Mapped[str] = mapped_column(
        Enum("reject", "replace", "warn", name="ban_action_enum"), default="reject"
    )
    replace_with: Mapped[str | None] = mapped_column(String(100), default="***")
    is_active: Mapped[int] = mapped_column(Integer, default=1)
    created_by: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("admins.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    __table_args__ = (Index("idx_bw_active", "is_active"),)
