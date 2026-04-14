"""管理端：用户管理 + 订阅管理"""
import logging

from fastapi import APIRouter, Depends

logger = logging.getLogger(__name__)
from pydantic import BaseModel
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import PageParams, get_current_admin
from app.models.user import User
from app.models.conversation import Conversation
from app.models.message import Message
from app.utils.response import fail, paginate, success

router = APIRouter(prefix="/api/admin/users", tags=["管理端-用户管理"])


class UpdateSubscribeBody(BaseModel):
    subscribe_plan: str | None = None
    subscribe_expire: str | None = None
    free_chats_left: int | None = None
    remark: str | None = None


class UpdateStatusBody(BaseModel):
    status: str
    reason: str | None = None


@router.get("")
async def list_users(
    keyword: str | None = None,
    status: str | None = None,
    subscribe_plan: str | None = None,
    admin: dict = Depends(get_current_admin),
    pager: PageParams = Depends(),
    db: AsyncSession = Depends(get_db),
):
    def _apply_filters(stmt):
        if keyword:
            stmt = stmt.where(
                or_(
                    User.nickname.contains(keyword),
                    User.phone.contains(keyword),
                    User.email.contains(keyword),
                )
            )
        if status:
            stmt = stmt.where(User.status == status)
        if subscribe_plan:
            stmt = stmt.where(User.subscribe_plan == subscribe_plan)
        return stmt

    total_stmt = _apply_filters(select(func.count()).select_from(User))
    total = (await db.execute(total_stmt)).scalar() or 0

    conv_counts = (
        select(
            Conversation.user_id.label("user_id"),
            func.count(Conversation.id).label("conversation_count"),
        )
        .group_by(Conversation.user_id)
        .subquery()
    )
    msg_counts = (
        select(
            Message.user_id.label("user_id"),
            func.count(Message.id).label("message_count"),
        )
        .group_by(Message.user_id)
        .subquery()
    )

    stmt = _apply_filters(
        select(
            User,
            func.coalesce(conv_counts.c.conversation_count, 0).label("conversation_count"),
            func.coalesce(msg_counts.c.message_count, 0).label("message_count"),
        )
        .outerjoin(conv_counts, conv_counts.c.user_id == User.id)
        .outerjoin(msg_counts, msg_counts.c.user_id == User.id)
    )
    rows = (
        await db.execute(
            stmt.order_by(User.created_at.desc()).offset(pager.offset).limit(pager.page_size)
        )
    ).all()
    items = [
        {
            "id": row.User.id,
            "nickname": row.User.nickname,
            "phone": row.User.phone,
            "email": row.User.email,
            "free_chats_left": row.User.free_chats_left,
            "subscribe_plan": row.User.subscribe_plan,
            "subscribe_expire": row.User.subscribe_expire.isoformat() if row.User.subscribe_expire else None,
            "status": row.User.status,
            "conversation_count": row.conversation_count,
            "message_count": row.message_count,
            "created_at": row.User.created_at.isoformat() if row.User.created_at else None,
        }
        for row in rows
    ]
    return success(paginate(items, total, pager.page, pager.page_size))


@router.put("/{user_id}/subscribe")
async def update_subscribe(
    user_id: int,
    body: UpdateSubscribeBody,
    admin: dict = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    if not user:
        return fail(1004, "用户不存在")
    if body.subscribe_plan is not None:
        user.subscribe_plan = body.subscribe_plan
    if body.subscribe_expire is not None:
        from datetime import datetime
        user.subscribe_expire = datetime.fromisoformat(body.subscribe_expire)
    if body.free_chats_left is not None:
        user.free_chats_left = body.free_chats_left
    return success({
        "id": user.id,
        "subscribe_plan": user.subscribe_plan,
        "subscribe_expire": user.subscribe_expire.isoformat() if user.subscribe_expire else None,
        "free_chats_left": user.free_chats_left,
    })


@router.put("/{user_id}/status")
async def update_status(
    user_id: int,
    body: UpdateStatusBody,
    admin: dict = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    if not user:
        return fail(1004, "用户不存在")
    user.status = body.status
    return success({"id": user.id, "status": user.status})
