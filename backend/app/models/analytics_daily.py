from datetime import date, datetime

from sqlalchemy import BigInteger, Date, DateTime, DECIMAL, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class AnalyticsDaily(Base):
    __tablename__ = "analytics_daily"

    stat_date: Mapped[date] = mapped_column(Date, primary_key=True)
    new_users: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    active_users: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    conversation_count: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    message_count: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    request_count: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    input_tokens: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    output_tokens: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    cost_usd: Mapped[float] = mapped_column(DECIMAL(18, 6), default=0, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
