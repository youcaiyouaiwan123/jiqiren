from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Enum, ForeignKey, Integer, JSON, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class PaymentConfig(Base):
    __tablename__ = "payment_config"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    channel: Mapped[str] = mapped_column(Enum("wechat", "alipay", name="pay_channel_enum"), nullable=False)
    merchant_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    api_key: Mapped[str | None] = mapped_column(String(500), nullable=True)
    api_secret: Mapped[str | None] = mapped_column(String(500), nullable=True)
    notify_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_active: Mapped[int] = mapped_column(Integer, default=0)
    extra_config: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    updated_by: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("admins.id"), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
