"""Subscription checkout and activation helpers."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Any
from urllib.parse import quote_plus
from uuid import uuid4

from app.models.payment import Payment
from app.models.payment_config import PaymentConfig
from app.models.plan import Plan
from app.models.user import User


def create_order_no() -> str:
    return f"SUB{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}{uuid4().hex[:16].upper()}"


def resolve_checkout_url(template: str | None, *, payment: Payment, plan: Plan) -> str:
    raw = (template or "").strip()
    if not raw:
        return ""
    mapping = {
        "{payment_id}": str(payment.id),
        "{order_no}": payment.order_no or "",
        "{plan_id}": str(plan.id),
        "{plan_type}": plan.type,
        "{plan_name}": quote_plus(plan.name),
        "{amount}": str(payment.amount or ""),
    }
    for key, value in mapping.items():
        raw = raw.replace(key, value)
    return raw


def serialize_payment_channel(row: PaymentConfig) -> dict[str, Any]:
    extra = row.extra_config or {}
    return {
        "id": row.id,
        "channel": row.channel,
        "display_name": extra.get("display_name") or row.channel,
        "description": extra.get("description") or "",
        "button_label": extra.get("button_label") or "立即支付",
        "qrcode_url": extra.get("qrcode_url") or "",
        "pay_tips": extra.get("pay_tips") or "",
        "checkout_url": extra.get("checkout_url") or "",
    }


def create_subscribe_payment(*, user_id: int, plan: Plan, channel: PaymentConfig) -> Payment:
    return Payment(
        user_id=user_id,
        type="subscribe",
        plan=plan.type if plan.type in {"monthly", "yearly"} else "monthly",
        plan_id=plan.id,
        channel=channel.channel,
        order_no=create_order_no(),
        amount=Decimal(str(plan.price)),
        status="pending",
    )


def apply_subscription_for_payment(*, user: User, plan: Plan, now: datetime | None = None) -> None:
    current = now or datetime.now(timezone.utc)
    if current.tzinfo is not None:
        current = current.replace(tzinfo=None)

    if plan.type not in {"monthly", "yearly"}:
        raise ValueError("Only monthly and yearly plans can be activated")

    if user.subscribe_expire and user.subscribe_expire > current:
        base_time = user.subscribe_expire
    else:
        base_time = current

    user.subscribe_plan = plan.type
    user.subscribe_expire = base_time + timedelta(days=int(plan.duration_days))
