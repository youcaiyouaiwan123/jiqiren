from datetime import date, datetime

from sqlalchemy import BigInteger, Date, DateTime, DECIMAL, PrimaryKeyConstraint, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class AnalyticsModelDaily(Base):
    __tablename__ = "analytics_model_daily"

    stat_date: Mapped[date] = mapped_column(Date, nullable=False)
    model: Mapped[str] = mapped_column(String(100), nullable=False)
    request_count: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    user_count: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    input_tokens: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    output_tokens: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    cost_usd: Mapped[float] = mapped_column(DECIMAL(18, 6), default=0, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        PrimaryKeyConstraint("stat_date", "model", name="pk_analytics_model_daily"),
    )
