from datetime import date, datetime

from sqlalchemy import BigInteger, Date, DateTime, Index, PrimaryKeyConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class AnalyticsUserDaily(Base):
    __tablename__ = "analytics_user_daily"

    stat_date: Mapped[date] = mapped_column(Date, nullable=False)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        PrimaryKeyConstraint("stat_date", "user_id", name="pk_analytics_user_daily"),
        Index("idx_analytics_user_daily_user_date", "user_id", "stat_date"),
    )
