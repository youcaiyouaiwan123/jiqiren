"""User subscription endpoints."""

import logging
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user_id
from app.models.payment import Payment
from app.models.payment_config import PaymentConfig
from app.models.plan import Plan
from app.models.redeem_code import RedeemCode
from app.models.user import User
from app.utils.crud import row_to_dict
from app.utils.response import fail, success
from app.services.subscription_service import (
    create_subscribe_payment,
    resolve_checkout_url,
    serialize_payment_channel,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/subscribe", tags=["用户端-订阅"])


def _serialize_payment(row: Payment, *, plan_name: str | None = None) -> dict:
    return {
        "id": row.id,
        "type": row.type,
        "plan": row.plan,
        "plan_id": row.plan_id,
        "plan_name": plan_name,
        "channel": row.channel,
        "order_no": row.order_no,
        "amount": row.amount,
        "status": row.status,
        "redeem_code": row.redeem_code,
        "remark": row.remark,
        "paid_at": row.paid_at.isoformat() if row.paid_at else None,
        "created_at": row.created_at.isoformat() if row.created_at else None,
        "updated_at": row.updated_at.isoformat() if row.updated_at else None,
    }


@router.get("/info")
async def subscribe_info(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    if not user:
        return fail(1004, "用户不存在")

    payments = (
        await db.execute(
            select(Payment)
            .where(Payment.user_id == user_id)
            .order_by(Payment.created_at.desc())
            .limit(10)
        )
    ).scalars().all()
    return success(
        {
            "subscribe_plan": user.subscribe_plan,
            "subscribe_expire": user.subscribe_expire.isoformat() if user.subscribe_expire else None,
            "free_chats_left": user.free_chats_left,
            "payments": [_serialize_payment(p) for p in payments],
        }
    )


@router.get("/catalog")
async def subscribe_catalog(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    if not user:
        return fail(1004, "用户不存在")

    plans = (
        await db.execute(
            select(Plan)
            .where(Plan.is_active == 1, Plan.type.in_(("monthly", "yearly")))
            .order_by(Plan.sort_order.asc(), Plan.id.asc())
        )
    ).scalars().all()
    channels = (
        await db.execute(
            select(PaymentConfig)
            .where(PaymentConfig.is_active == 1)
            .order_by(PaymentConfig.id.asc())
        )
    ).scalars().all()

    return success(
        {
            "current": {
                "subscribe_plan": user.subscribe_plan,
                "subscribe_expire": user.subscribe_expire.isoformat() if user.subscribe_expire else None,
                "free_chats_left": user.free_chats_left,
            },
            "plans": [row_to_dict(plan) for plan in plans],
            "channels": [serialize_payment_channel(channel) for channel in channels],
        }
    )


@router.get("/orders")
async def list_subscribe_orders(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    rows = (
        await db.execute(
            select(Payment, Plan.name.label("plan_name"))
            .outerjoin(Plan, Plan.id == Payment.plan_id)
            .where(Payment.user_id == user_id, Payment.type == "subscribe")
            .order_by(Payment.created_at.desc())
            .limit(20)
        )
    ).all()
    return success(
        {
            "list": [
                _serialize_payment(row.Payment, plan_name=getattr(row, "plan_name", None))
                for row in rows
            ]
        }
    )


class CheckoutBody(BaseModel):
    plan_id: int
    channel_id: int


@router.post("/checkout")
async def checkout_subscribe(
    body: CheckoutBody,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    if not user:
        return fail(1004, "用户不存在")

    plan = (
        await db.execute(
            select(Plan).where(Plan.id == body.plan_id, Plan.is_active == 1, Plan.type.in_(("monthly", "yearly")))
        )
    ).scalar_one_or_none()
    if not plan:
        return fail(1004, "套餐不存在或未上架")

    channel = (
        await db.execute(
            select(PaymentConfig).where(PaymentConfig.id == body.channel_id, PaymentConfig.is_active == 1)
        )
    ).scalar_one_or_none()
    if not channel:
        return fail(1004, "支付渠道不存在或未启用")

    payment = create_subscribe_payment(user_id=user_id, plan=plan, channel=channel)
    db.add(payment)
    await db.flush()

    checkout_url = resolve_checkout_url(
        (plan.display_config or {}).get("cta_url") or (channel.extra_config or {}).get("checkout_url"),
        payment=payment,
        plan=plan,
    )
    logger.info(
        "[订阅下单] 创建成功 | user_id=%s plan_id=%s channel=%s payment_id=%s order_no=%s",
        user_id,
        plan.id,
        channel.channel,
        payment.id,
        payment.order_no,
    )
    return success(
        {
            "payment": _serialize_payment(payment, plan_name=plan.name),
            "plan": row_to_dict(plan),
            "channel": serialize_payment_channel(channel),
            "checkout_url": checkout_url,
        }
    )


class RedeemBody(BaseModel):
    code: str


@router.post("/redeem")
async def redeem(
    body: RedeemBody,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    if not user:
        return fail(1004, "用户不存在")

    now = datetime.now(timezone.utc)
    redeem_code = (
        await db.execute(
            select(RedeemCode).where(
                RedeemCode.code == body.code,
                RedeemCode.status == "unused",
            )
        )
    ).scalar_one_or_none()
    if not redeem_code:
        logger.info("[兑换] 无效兑换码 | user_id=%s code=%s", user_id, body.code)
        return fail(1004, "兑换码无效或已过期")
    if redeem_code.expire_at and redeem_code.expire_at < now:
        logger.info("[兑换] 兑换码已过期 | user_id=%s code=%s", user_id, body.code)
        return fail(1004, "兑换码无效或已过期")

    if redeem_code.type == "days":
        base_time = max(now, user.subscribe_expire) if user.subscribe_expire and user.subscribe_expire > now else now
        user.subscribe_expire = base_time + timedelta(days=redeem_code.value)
        if user.subscribe_plan == "free":
            user.subscribe_plan = "monthly"
        message = f"兑换成功，已增加 {redeem_code.value} 天会员时长"
    else:
        user.free_chats_left = (user.free_chats_left or 0) + redeem_code.value
        message = f"兑换成功，已增加 {redeem_code.value} 次免费对话"

    redeem_code.status = "used"
    redeem_code.used_by = user_id
    redeem_code.used_at = now

    payment = Payment(user_id=user_id, type="redeem", redeem_code=redeem_code.code, status="success")
    db.add(payment)
    await db.flush()

    logger.info(
        "[兑换] 成功 | user_id=%s code=%s type=%s value=%s",
        user_id,
        redeem_code.code,
        redeem_code.type,
        redeem_code.value,
    )

    return success(
        {
            "type": redeem_code.type,
            "value": redeem_code.value,
            "message": message,
            "subscribe_plan": user.subscribe_plan,
            "subscribe_expire": user.subscribe_expire.isoformat() if user.subscribe_expire else None,
            "free_chats_left": user.free_chats_left,
        }
    )
