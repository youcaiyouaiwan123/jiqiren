from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Enum, ForeignKey, Integer, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ExpireReminderConfig(Base):
    __tablename__ = "expire_reminder_config"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    days_before: Mapped[int] = mapped_column(Integer, nullable=False)
    channel: Mapped[str] = mapped_column(
        Enum("site", "sms", "email", name="reminder_channel_enum"), nullable=False
    )
    template: Mapped[str] = mapped_column(Text, nullable=False)
    is_active: Mapped[int] = mapped_column(Integer, default=1)
    created_by: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("admins.id"), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
