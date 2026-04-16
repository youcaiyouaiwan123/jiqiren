from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Enum, Index, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    phone: Mapped[str | None] = mapped_column(String(20), unique=True, nullable=True)
    email: Mapped[str | None] = mapped_column(String(100), unique=True, nullable=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    nickname: Mapped[str | None] = mapped_column(String(50))
    avatar_url: Mapped[str | None] = mapped_column(String(500))
    remark: Mapped[str | None] = mapped_column(String(200), nullable=True)
    free_chats_left: Mapped[int] = mapped_column(Integer, default=3)
    subscribe_plan: Mapped[str] = mapped_column(
        Enum("free", "monthly", "yearly", name="subscribe_plan_enum"), default="free"
    )
    subscribe_expire: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    status: Mapped[str] = mapped_column(
        Enum("active", "banned", name="user_status_enum"), default="active"
    )
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index("idx_phone", "phone"),
        Index("idx_status", "status"),
        Index("idx_user_deleted_at", "deleted_at"),
        Index("idx_user_created_at", "created_at"),
        Index("idx_user_subscribe_plan", "subscribe_plan"),
    )
