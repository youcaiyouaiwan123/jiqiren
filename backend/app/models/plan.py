from datetime import datetime

from sqlalchemy import BigInteger, DateTime, DECIMAL, Enum, Integer, JSON, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Plan(Base):
    __tablename__ = "plans"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    type: Mapped[str] = mapped_column(
        Enum("monthly", "yearly", "custom", name="plan_type_enum"), nullable=False
    )
    price: Mapped[float] = mapped_column(DECIMAL(10, 2), nullable=False)
    duration_days: Mapped[int] = mapped_column(Integer, nullable=False)
    chat_limit: Mapped[int] = mapped_column(Integer, default=-1)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    display_config: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    is_active: Mapped[int] = mapped_column(Integer, default=1)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
