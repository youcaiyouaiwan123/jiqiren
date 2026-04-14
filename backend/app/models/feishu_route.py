from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Integer, JSON, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class FeishuRoute(Base):
    __tablename__ = "feishu_routes"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    app_id: Mapped[str] = mapped_column(String(100), nullable=False)
    app_secret: Mapped[str] = mapped_column(String(200), nullable=False)
    app_token: Mapped[str] = mapped_column(String(100), nullable=False)
    table_id: Mapped[str] = mapped_column(String(100), nullable=False)
    route_rule: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    is_active: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
