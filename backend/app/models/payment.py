from datetime import datetime

from sqlalchemy import BigInteger, DateTime, DECIMAL, Enum, ForeignKey, Index, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)
    type: Mapped[str] = mapped_column(Enum("subscribe", "redeem", name="payment_type_enum"), nullable=False)
    plan: Mapped[str | None] = mapped_column(Enum("monthly", "yearly", name="payment_plan_enum"), nullable=True)
    plan_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("plans.id"), nullable=True)
    channel: Mapped[str | None] = mapped_column(String(20), nullable=True)
    order_no: Mapped[str | None] = mapped_column(String(64), nullable=True)
    amount: Mapped[float | None] = mapped_column(DECIMAL(10, 2), nullable=True)
    redeem_code: Mapped[str | None] = mapped_column(String(50), nullable=True)
    remark: Mapped[str | None] = mapped_column(String(200), nullable=True)
    status: Mapped[str] = mapped_column(
        Enum("pending", "success", "failed", name="payment_status_enum"), default="pending"
    )
    paid_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index("idx_pay_user", "user_id"),
        Index("idx_pay_order_no", "order_no"),
        Index("idx_pay_status_created", "status", "created_at"),
        UniqueConstraint("order_no", name="uq_pay_order_no"),
    )
