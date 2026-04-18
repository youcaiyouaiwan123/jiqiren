"""Admin subscription payment review."""

import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import and_, func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import PageParams, get_current_admin
from app.models.payment import Payment
from app.models.plan import Plan
from app.models.user import User
from app.services.subscription_service import apply_subscription_for_payment
from app.utils.response import fail, paginate, success

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/admin/payments", tags=["管理端-订阅订单"])


class PaymentReviewBody(BaseModel):
    remark: str | None = None


def _serialize_payment_row(row) -> dict:
    payment = row.Payment
    plan = getattr(row, "Plan", None)
    return {
        "id": payment.id,
        "order_no": payment.order_no,
        "user_id": payment.user_id,
        "nickname": getattr(row, "nickname", None),
        "phone": getattr(row, "phone", None),
        "email": getattr(row, "email", None),
        "type": payment.type,
        "plan": payment.plan,
        "plan_id": payment.plan_id,
        "plan_name": getattr(row, "plan_name", None) or (plan.name if plan else None),
        "channel": payment.channel,
        "amount": payment.amount,
        "status": payment.status,
        "remark": payment.remark,
        "paid_at": payment.paid_at.isoformat() if payment.paid_at else None,
        "created_at": payment.created_at.isoformat() if payment.created_at else None,
        "updated_at": payment.updated_at.isoformat() if payment.updated_at else None,
    }


@router.get("")
async def list_payments(
    keyword: str | None = None,
    status: str | None = None,
    channel: str | None = None,
    admin: dict = Depends(get_current_admin),
    pager: PageParams = Depends(),
    db: AsyncSession = Depends(get_db),
):
    filters = [Payment.type == "subscribe"]
    if status:
        filters.append(Payment.status == status)
    if channel:
        filters.append(Payment.channel == channel)
    if keyword:
        filters.append(
            or_(
                Payment.order_no.contains(keyword, autoescape=True),
                User.nickname.contains(keyword, autoescape=True),
                User.phone.contains(keyword, autoescape=True),
                User.email.contains(keyword, autoescape=True),
            )
        )

    base_stmt = (
        select(Payment, User.nickname.label("nickname"), User.phone.label("phone"), User.email.label("email"), Plan.name.label("plan_name"))
        .join(User, User.id == Payment.user_id)
        .outerjoin(Plan, Plan.id == Payment.plan_id)
        .where(and_(*filters))
    )
    total = (await db.execute(select(func.count()).select_from(base_stmt.subquery()))).scalar() or 0
    rows = (
        await db.execute(
            base_stmt.order_by(Payment.created_at.desc()).offset(pager.offset).limit(pager.page_size)
        )
    ).all()
    return success(paginate([_serialize_payment_row(row) for row in rows], total, pager.page, pager.page_size))


@router.put("/{payment_id}/approve")
async def approve_payment(
    payment_id: int,
    body: PaymentReviewBody,
    admin: dict = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    payment = (
        await db.execute(
            select(Payment)
            .where(Payment.id == payment_id, Payment.type == "subscribe")
            .with_for_update()
        )
    ).scalar_one_or_none()
    if not payment:
        return fail(1004, "订单不存在")
    if payment.status == "success":
        return fail(1001, "订单已处理")
    if not payment.plan_id:
        return fail(1001, "订单缺少套餐信息")

    user = (
        await db.execute(select(User).where(User.id == payment.user_id).with_for_update())
    ).scalar_one_or_none()
    plan = await db.get(Plan, payment.plan_id)
    if not user or not plan:
        return fail(1004, "订单关联数据不存在")

    apply_subscription_for_payment(user=user, plan=plan, now=datetime.now(timezone.utc))
    payment.status = "success"
    payment.paid_at = datetime.now(timezone.utc)
    payment.remark = (body.remark or "").strip() or payment.remark
    await db.flush()

    logger.info(
        "[订阅订单] 审核通过 | admin_id=%s payment_id=%s user_id=%s plan_id=%s",
        admin["admin_id"],
        payment.id,
        user.id,
        plan.id,
    )
    return success(
        {
            "payment_id": payment.id,
            "status": payment.status,
            "subscribe_plan": user.subscribe_plan,
            "subscribe_expire": user.subscribe_expire.isoformat() if user.subscribe_expire else None,
        }
    )


@router.put("/{payment_id}/reject")
async def reject_payment(
    payment_id: int,
    body: PaymentReviewBody,
    admin: dict = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    payment = await db.get(Payment, payment_id)
    if not payment or payment.type != "subscribe":
        return fail(1004, "订单不存在")
    if payment.status == "success":
        return fail(1001, "已成功订单不能驳回")

    payment.status = "failed"
    payment.remark = (body.remark or "").strip() or payment.remark
    await db.flush()
    logger.info("[订阅订单] 驳回 | admin_id=%s payment_id=%s", admin["admin_id"], payment.id)
    return success({"payment_id": payment.id, "status": payment.status, "remark": payment.remark})
