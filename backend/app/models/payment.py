from datetime import datetime

from sqlalchemy import BigInteger, DateTime, DECIMAL, Enum, ForeignKey, Index, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)
    type: Mapped[str] = mapped_column(Enum("subscribe", "redeem", name="payment_type_enum"), nullable=False)
    plan: Mapped[str | None] = mapped_column(Enum("monthly", "yearly", name="payment_plan_enum"), nullable=True)
    amount: Mapped[float | None] = mapped_column(DECIMAL(10, 2), nullable=True)
    redeem_code: Mapped[str | None] = mapped_column(String(50), nullable=True)
    status: Mapped[str] = mapped_column(
        Enum("pending", "success", "failed", name="payment_status_enum"), default="pending"
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    __table_args__ = (Index("idx_pay_user", "user_id"),)
