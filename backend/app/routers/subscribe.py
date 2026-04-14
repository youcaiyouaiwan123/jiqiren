"""用户端：订阅信息 + 兑换码"""
import logging
from datetime import datetime, timedelta, timezone

logger = logging.getLogger(__name__)

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user_id
from app.models.payment import Payment
from app.models.redeem_code import RedeemCode
from app.models.user import User
from app.utils.response import fail, success

router = APIRouter(prefix="/api/subscribe", tags=["用户端-订阅"])


@router.get("/info")
async def subscribe_info(user_id: int = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    user = await db.get(User, user_id)
    if not user:
        return fail(1004, "用户不存在")
    # 最近支付记录
    payments = (
        await db.execute(
            select(Payment)
            .where(Payment.user_id == user_id)
            .order_by(Payment.created_at.desc())
            .limit(10)
        )
    ).scalars().all()
    from app.utils.crud import row_to_dict
    return success({
        "subscribe_plan": user.subscribe_plan,
        "subscribe_expire": user.subscribe_expire.isoformat() if user.subscribe_expire else None,
        "free_chats_left": user.free_chats_left,
        "payments": [row_to_dict(p) for p in payments],
    })


class RedeemBody(BaseModel):
    code: str


@router.post("/redeem")
async def redeem(body: RedeemBody, user_id: int = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    user = await db.get(User, user_id)
    if not user:
        return fail(1004, "用户不存在")
    now = datetime.now(timezone.utc)
    rc = (
        await db.execute(
            select(RedeemCode).where(
                RedeemCode.code == body.code,
                RedeemCode.status == "unused",
            )
        )
    ).scalar_one_or_none()
    if not rc:
        logger.info("[兑换] 无效兑换码 | user_id=%s code=%s", user_id, body.code)
        return fail(1004, "兑换码无效或已过期")
    if rc.expire_at and rc.expire_at < now:
        logger.info("[兑换] 兑换码已过期 | user_id=%s code=%s", user_id, body.code)
        return fail(1004, "兑换码无效或已过期")

    # 根据类型更新用户
    if rc.type == "days":
        base_time = max(now, user.subscribe_expire) if user.subscribe_expire and user.subscribe_expire > now else now
        user.subscribe_expire = base_time + timedelta(days=rc.value)
        if user.subscribe_plan == "free":
            user.subscribe_plan = "monthly"
        msg = f"兑换成功，已增加 {rc.value} 天会员时长"
    else:
        user.free_chats_left = (user.free_chats_left or 0) + rc.value
        msg = f"兑换成功，已增加 {rc.value} 次免费对话"

    # 更新兑换码
    rc.status = "used"
    rc.used_by = user_id
    rc.used_at = now

    # 写入支付记录
    payment = Payment(user_id=user_id, type="redeem", redeem_code=rc.code, status="success")
    db.add(payment)
    await db.flush()
    logger.info("[兑换] 成功 | user_id=%s code=%s type=%s value=%s", user_id, rc.code, rc.type, rc.value)

    return success({
        "type": rc.type,
        "value": rc.value,
        "message": msg,
        "subscribe_plan": user.subscribe_plan,
        "subscribe_expire": user.subscribe_expire.isoformat() if user.subscribe_expire else None,
        "free_chats_left": user.free_chats_left,
    })
