"""管理端：用户管理 + 订阅管理"""
import logging
from datetime import datetime

from fastapi import APIRouter, Depends

logger = logging.getLogger(__name__)
from pydantic import BaseModel
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import PageParams, get_current_admin
from app.core.security import hash_password
from app.models.conversation import Conversation
from app.models.message import Message
from app.models.register_config import RegisterConfig
from app.models.user import User
from app.utils.response import fail, paginate, success

router = APIRouter(prefix="/api/admin/users", tags=["管理端-用户管理"])

VALID_SUBSCRIBE_PLANS = {"free", "monthly", "yearly"}
VALID_USER_STATUS = {"active", "banned"}
VALID_TRIAL_MODES = {"set", "increase", "decrease", "reset_default"}

class CreateUserBody(BaseModel):
    phone: str | None = None
    email: str | None = None
    password: str
    nickname: str | None = None
    remark: str | None = None
    subscribe_plan: str | None = "free"
    subscribe_expire: str | None = None
    free_chats_left: int | None = None

class UpdateUserBody(BaseModel):
    nickname: str | None = None
    phone: str | None = None
    email: str | None = None
    remark: str | None = None

class UpdateSubscribeBody(BaseModel):
    subscribe_plan: str | None = None
    subscribe_expire: str | None = None

class UpdateTrialBody(BaseModel):
    mode: str
    value: int | None = None

class UpdateStatusBody(BaseModel):
    status: str
    reason: str | None = None

def _normalize_phone(phone: str | None) -> str | None:
    if phone is None:
        return None
    normalized = phone.strip().replace(" ", "")
    return normalized or None

def _normalize_email(email: str | None) -> str | None:
    if email is None:
        return None
    normalized = email.strip().lower()
    return normalized or None

def _normalize_text(value: str | None, limit: int) -> str | None:
    if value is None:
        return None
    normalized = value.strip()
    if not normalized:
        return None
    return normalized[:limit]

def _parse_datetime_or_none(raw_value: str | None) -> tuple[datetime | None, str | None]:
    if raw_value is None:
        return None, None
    normalized = raw_value.strip()
    if not normalized:
        return None, None
    try:
        return datetime.fromisoformat(normalized), None
    except ValueError:
        return None, "到期时间格式错误"

def _serialize_user(user: User, conversation_count: int = 0, message_count: int = 0) -> dict:
    return {
        "id": user.id,
        "nickname": user.nickname,
        "phone": user.phone,
        "email": user.email,
        "remark": user.remark,
        "free_chats_left": user.free_chats_left,
        "subscribe_plan": user.subscribe_plan,
        "subscribe_expire": user.subscribe_expire.isoformat() if user.subscribe_expire else None,
        "status": user.status,
        "conversation_count": conversation_count,
        "message_count": message_count,
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "deleted_at": user.deleted_at.isoformat() if user.deleted_at else None,
    }

async def _get_default_free_chats(db: AsyncSession) -> int:
    row = (
        await db.execute(
            select(RegisterConfig).where(RegisterConfig.config_key == "default_free_chats")
        )
    ).scalar_one_or_none()
    if not row or row.config_value is None:
        return 3
    try:
        return max(int(row.config_value), 0)
    except (TypeError, ValueError):
        return 3

async def _ensure_unique_identity(
    db: AsyncSession,
    *,
    phone: str | None,
    email: str | None,
    exclude_user_id: int | None = None,
):
    if phone:
        stmt = select(User.id).where(User.phone == phone, User.deleted_at.is_(None))
        if exclude_user_id is not None:
            stmt = stmt.where(User.id != exclude_user_id)
        exists = (await db.execute(stmt)).scalar_one_or_none()
        if exists:
            return fail(1005, "该手机号已注册")
    if email:
        stmt = select(User.id).where(User.email == email, User.deleted_at.is_(None))
        if exclude_user_id is not None:
            stmt = stmt.where(User.id != exclude_user_id)
        exists = (await db.execute(stmt)).scalar_one_or_none()
        if exists:
            return fail(1005, "该邮箱已注册")
    return None

async def _get_user_or_fail(db: AsyncSession, user_id: int, *, allow_deleted: bool = False):
    user = await db.get(User, user_id)
    if not user or (not allow_deleted and user.deleted_at is not None):
        return None, fail(1004, "用户不存在")
    return user, None

@router.post("")
async def create_user(
    body: CreateUserBody,
    admin: dict = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    phone = _normalize_phone(body.phone)
    email = _normalize_email(body.email)
    nickname = _normalize_text(body.nickname, 50)
    remark = _normalize_text(body.remark, 200)
    plan = (body.subscribe_plan or "free").strip().lower()

    if not phone and not email:
        return fail(1001, "请至少填写手机号或邮箱")
    if len(body.password.strip()) < 6:
        return fail(1001, "密码长度不能少于 6 位")
    if plan not in VALID_SUBSCRIBE_PLANS:
        return fail(1001, "订阅计划不支持")

    duplicate_error = await _ensure_unique_identity(db, phone=phone, email=email)
    if duplicate_error:
        return duplicate_error

    subscribe_expire, expire_error = _parse_datetime_or_none(body.subscribe_expire)
    if expire_error:
        return fail(1005, expire_error)

    default_free_chats = await _get_default_free_chats(db)
    free_chats_left = max(body.free_chats_left if body.free_chats_left is not None else default_free_chats, 0)
    nickname_seed = phone or email or str(int(datetime.now().timestamp()))
    if "@" in nickname_seed:
        nickname_seed = nickname_seed.split("@", 1)[0]
    nickname = nickname or f"用户{nickname_seed[-4:]}"

    user = User(
        phone=phone,
        email=email,
        password_hash=hash_password(body.password.strip()),
        nickname=nickname,
        remark=remark,
        free_chats_left=free_chats_left,
        subscribe_plan=plan,
        subscribe_expire=None if plan == "free" else subscribe_expire,
        status="active",
    )
    db.add(user)
    await db.flush()
    logger.info("[管理端-用户] 新建用户 | admin_id=%s user_id=%s", admin["admin_id"], user.id)
    return success(_serialize_user(user), "创建成功")

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
                    User.remark.contains(keyword),
                )
            )
        if status == "deleted":
            stmt = stmt.where(User.deleted_at.is_not(None))
        else:
            stmt = stmt.where(User.deleted_at.is_(None))
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
        _serialize_user(row.User, row.conversation_count, row.message_count)
        for row in rows
    ]
    return success(paginate(items, total, pager.page, pager.page_size))


@router.put("/{user_id}")
async def update_user(
    user_id: int,
    body: UpdateUserBody,
    admin: dict = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    user, err = await _get_user_or_fail(db, user_id)
    if err:
        return err

    phone = _normalize_phone(body.phone)
    email = _normalize_email(body.email)
    nickname = _normalize_text(body.nickname, 50)
    remark = _normalize_text(body.remark, 200)

    if not phone and not email:
        return fail(1001, "请至少保留手机号或邮箱中的一个")

    duplicate_error = await _ensure_unique_identity(
        db,
        phone=phone,
        email=email,
        exclude_user_id=user.id,
    )
    if duplicate_error:
        return duplicate_error

    user.phone = phone
    user.email = email
    user.nickname = nickname or user.nickname or f"用户{user.id}"
    user.remark = remark

    logger.info("[管理端-用户] 更新资料 | admin_id=%s user_id=%s", admin["admin_id"], user.id)
    return success(_serialize_user(user), "更新成功")

@router.put("/{user_id}/subscribe")
async def update_subscribe(
    user_id: int,
    body: UpdateSubscribeBody,
    admin: dict = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    user, err = await _get_user_or_fail(db, user_id)
    if err:
        return err
    if body.subscribe_plan is not None:
        plan = body.subscribe_plan.strip().lower()
        if plan not in VALID_SUBSCRIBE_PLANS:
            return fail(1001, "订阅计划不支持")
        user.subscribe_plan = plan
        if plan == "free":
            user.subscribe_expire = None
    if body.subscribe_expire is not None:
        parsed_expire, expire_error = _parse_datetime_or_none(body.subscribe_expire)
        if expire_error:
            return fail(1005, expire_error)
        user.subscribe_expire = parsed_expire
    if user.subscribe_plan == "free":
        user.subscribe_expire = None
    logger.info("[管理端-用户] 更新会员 | admin_id=%s user_id=%s", admin["admin_id"], user.id)
    return success({
        "id": user.id,
        "subscribe_plan": user.subscribe_plan,
        "subscribe_expire": user.subscribe_expire.isoformat() if user.subscribe_expire else None,
    }, "更新成功")

@router.put("/{user_id}/status")
async def update_status(
    user_id: int,
    body: UpdateStatusBody,
    admin: dict = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    user, err = await _get_user_or_fail(db, user_id)
    if err:
        return err
    status = body.status.strip().lower()
    if status not in VALID_USER_STATUS:
        return fail(1001, "用户状态不支持")
    user.status = status
    logger.info("[管理端-用户] 更新状态 | admin_id=%s user_id=%s status=%s", admin["admin_id"], user.id, status)
    return success({"id": user.id, "status": user.status}, "更新成功")


@router.put("/{user_id}/trial")
async def update_trial(
    user_id: int,
    body: UpdateTrialBody,
    admin: dict = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    user, err = await _get_user_or_fail(db, user_id)
    if err:
        return err

    mode = body.mode.strip().lower()
    if mode not in VALID_TRIAL_MODES:
        return fail(1001, "试用控制方式不支持")

    current = max(user.free_chats_left or 0, 0)
    default_free_chats = await _get_default_free_chats(db)

    if mode == "reset_default":
        next_value = default_free_chats
    else:
        if body.value is None or body.value < 0:
            return fail(1001, "请填写正确的试用次数")
        if mode == "set":
            next_value = body.value
        elif mode == "increase":
            next_value = current + body.value
        else:
            next_value = max(current - body.value, 0)

    user.free_chats_left = next_value
    logger.info(
        "[管理端-用户] 更新试用次数 | admin_id=%s user_id=%s mode=%s value=%s result=%s",
        admin["admin_id"],
        user.id,
        mode,
        body.value,
        next_value,
    )
    return success({
        "id": user.id,
        "free_chats_left": user.free_chats_left,
        "default_free_chats": default_free_chats,
    }, "更新成功")


@router.delete("/{user_id}")
async def soft_delete_user(
    user_id: int,
    admin: dict = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    user, err = await _get_user_or_fail(db, user_id)
    if err:
        return err

    deleted_at = datetime.now()
    origin_parts: list[str] = []
    if user.phone:
        origin_parts.append(f"原手机号:{user.phone}")
    if user.email:
        origin_parts.append(f"原邮箱:{user.email}")
    delete_note = f"已注销 {deleted_at.strftime('%Y-%m-%d %H:%M:%S')}"
    if origin_parts:
        delete_note = f"{delete_note}；{'；'.join(origin_parts)}"
    merged_remark = "；".join(part for part in [user.remark, delete_note] if part)

    user.phone = None
    user.email = None
    user.status = "banned"
    user.deleted_at = deleted_at
    user.remark = merged_remark[:200] if merged_remark else None

    logger.info("[管理端-用户] 注销用户 | admin_id=%s user_id=%s", admin["admin_id"], user.id)
    return success({
        "id": user.id,
        "deleted_at": user.deleted_at.isoformat() if user.deleted_at else None,
    }, "用户已注销")
