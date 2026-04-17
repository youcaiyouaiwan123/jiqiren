"""管理端认证：登录 / 改密 / 防爆破"""
import logging
import re
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import BizException, get_current_admin
from app.core.redis import get_redis, atomic_incr
from app.core.security import create_access_token, create_refresh_token, decode_token, hash_password, verify_password
from app.models.admin import Admin
from app.utils.response import fail, success

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/admin", tags=["管理端认证"])

# ── 防爆破参数 ────────────────────────────────────────────────────────────────
# 同一账号：连续失败 N 次后锁定
_LOCK_TIERS = [
    (5,  15 * 60),   # 5  次失败 → 锁 15 分钟
    (10, 60 * 60),   # 10 次失败 → 锁 60 分钟
    (20, 24 * 60 * 60),  # 20 次失败 → 锁 24 小时
]
_FAIL_WINDOW   = 30 * 60   # 失败计数窗口：30 分钟
_MAX_FAIL_KEY  = "admin_login_fail:{username}"
_LOCKED_KEY    = "admin_locked:{username}"

# 同一 IP：每小时最多 _IP_MAX_ATTEMPTS 次登录尝试
_IP_MAX_ATTEMPTS = 40
_IP_WINDOW       = 60 * 60
_IP_FAIL_KEY     = "admin_login_ip:{ip}"


def _client_ip(request: Request) -> str:
    xff = (request.headers.get("x-forwarded-for") or "").split(",", 1)[0].strip()
    return xff or (request.client.host if request.client else "unknown")


def _lock_ttl(fail_count: int) -> int:
    """根据累计失败次数返回应锁定的秒数，0 = 不锁"""
    for threshold, seconds in reversed(_LOCK_TIERS):
        if fail_count >= threshold:
            return seconds
    return 0


# ── 密码复杂度 ────────────────────────────────────────────────────────────────
_PWD_MIN_LEN    = 12
_PWD_PATTERN    = re.compile(
    r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()\-_=+\[\]{};:'\",.<>?/\\|`~]).{12,}$"
)

def _validate_password_strength(password: str) -> str | None:
    """返回错误描述字符串，None 表示合格"""
    if len(password) < _PWD_MIN_LEN:
        return f"密码不能少于 {_PWD_MIN_LEN} 位"
    if not re.search(r"[a-z]", password):
        return "密码必须包含小写字母"
    if not re.search(r"[A-Z]", password):
        return "密码必须包含大写字母"
    if not re.search(r"\d", password):
        return "密码必须包含数字"
    if not re.search(r"[!@#$%^&*()\-_=+\[\]{};:'\",.<>?/\\|`~]", password):
        return "密码必须包含特殊字符（如 !@#$%^&*）"
    return None


# ── Schemas ───────────────────────────────────────────────────────────────────

class AdminLoginBody(BaseModel):
    username: str
    password: str


class ChangePasswordBody(BaseModel):
    old_password: str
    new_password: str


# ── Routes ───────────────────────────────────────────────────────────────────

@router.post("/login")
async def admin_login(body: AdminLoginBody, request: Request, db: AsyncSession = Depends(get_db)):
    ip = _client_ip(request)
    username = body.username.strip()

    redis = get_redis(required=False)

    # ── IP 频率限制 ──
    if redis:
        ip_key = _IP_FAIL_KEY.format(ip=ip)
        ip_count = await atomic_incr(redis, ip_key, _IP_WINDOW)
        if ip_count > _IP_MAX_ATTEMPTS:
            ttl = max(await redis.ttl(ip_key), 1)
            logger.warning("[管理登录] IP 超频被拦截 | ip=%s count=%s", ip, ip_count)
            return fail(1029, f"当前 IP 请求过于频繁，请 {ttl // 60 + 1} 分钟后重试")

    # ── 账号锁定检查 ──
    if redis:
        locked_key = _LOCKED_KEY.format(username=username)
        locked_ttl = await redis.ttl(locked_key)
        if locked_ttl and locked_ttl > 0:
            mins = locked_ttl // 60 + 1
            logger.warning("[管理登录] 账号已锁定 | username=%s ttl=%ss ip=%s", username, locked_ttl, ip)
            return fail(1030, f"账号已锁定，请 {mins} 分钟后再试")

    # ── 查库（统一错误信息，防止用户名枚举）──
    admin = (await db.execute(select(Admin).where(Admin.username == username))).scalar_one_or_none()
    pwd_ok = admin is not None and verify_password(body.password, admin.password_hash)

    if not pwd_ok:
        logger.warning("[管理登录] 认证失败 | username=%s ip=%s", username, ip)
        # 记录失败次数（pipeline 保证 INCR+EXPIRE 原子执行，每次失败都重置窗口防卡点攻击）
        if redis:
            fail_key = _MAX_FAIL_KEY.format(username=username)
            async with redis.pipeline(transaction=True) as pipe:
                pipe.incr(fail_key)
                pipe.expire(fail_key, _FAIL_WINDOW)
                results = await pipe.execute()
            fail_count = int(results[0])
            lock_secs = _lock_ttl(fail_count)
            if lock_secs:
                locked_key = _LOCKED_KEY.format(username=username)
                await redis.set(locked_key, "1", ex=lock_secs)
                await redis.delete(fail_key)
                mins = lock_secs // 60
                logger.warning("[管理登录] 账号触发锁定 | username=%s fail_count=%s lock=%ss ip=%s",
                               username, fail_count, lock_secs, ip)
                return fail(1030, f"连续登录失败次数过多，账号已锁定 {mins} 分钟")
        # 统一错误信息（不区分账号不存在 / 密码错误）
        return fail(1001, "用户名或密码错误")

    # ── 登录成功：清除失败计数 ──
    if redis:
        await redis.delete(_MAX_FAIL_KEY.format(username=username))

    logger.info("[管理登录] 成功 | admin_id=%s username=%s ip=%s", admin.id, admin.username, ip)

    token_data = {"admin_id": admin.id, "role": "admin", "admin_role": admin.role}
    return success({
        "access_token": create_access_token(token_data),
        "refresh_token": create_refresh_token(token_data),
        "token_type": "bearer",
        "expires_in": 7200,
        "admin": {"id": admin.id, "username": admin.username, "role": admin.role},
    })


class AdminRefreshBody(BaseModel):
    refresh_token: str


@router.post("/refresh")
async def admin_refresh_token(body: AdminRefreshBody):
    payload = decode_token(body.refresh_token)
    if not payload or payload.get("type") != "refresh" or payload.get("role") != "admin":
        return fail(1002, "refresh_token 无效或已过期")
    token_data = {
        "admin_id": payload["admin_id"],
        "role": "admin",
        "admin_role": payload.get("admin_role", "admin"),
    }
    return success({
        "access_token": create_access_token(token_data),
        "refresh_token": create_refresh_token(token_data),
        "token_type": "bearer",
        "expires_in": 2592000,
    })


@router.post("/change-password")
async def change_password(
    body: ChangePasswordBody,
    current_admin: dict = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """管理员修改自己的密码（需登录）"""
    # 新密码复杂度
    err = _validate_password_strength(body.new_password)
    if err:
        return fail(1031, err)

    admin = await db.get(Admin, current_admin["admin_id"])
    if not admin:
        return fail(1004, "管理员不存在")

    if not verify_password(body.old_password, admin.password_hash):
        return fail(1001, "原密码错误")

    if body.old_password == body.new_password:
        return fail(1032, "新密码不能与原密码相同")

    admin.password_hash = hash_password(body.new_password)
    logger.info("[管理改密] 成功 | admin_id=%s username=%s", admin.id, admin.username)
    return success({"message": "密码已修改，请重新登录"})


@router.get("/profile")
async def admin_profile(current_admin: dict = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    admin = await db.get(Admin, current_admin["admin_id"])
    if not admin:
        return fail(1004, "管理员不存在")
    return success({
        "id": admin.id,
        "username": admin.username,
        "role": admin.role,
        "created_at": admin.created_at.isoformat() if admin.created_at else None,
    })


@router.post("/unlock-admin")
async def unlock_admin(
    body: AdminLoginBody,  # 复用，只用 username 字段
    current_admin: dict = Depends(get_current_admin),
):
    """super 管理员手动解锁被锁账号"""
    if current_admin.get("role") != "super":
        raise BizException(1003, "仅超级管理员可操作")
    redis = get_redis(required=False)
    if not redis:
        return fail(5003, "Redis 不可用")
    username = body.username.strip()
    locked_key = _LOCKED_KEY.format(username=username)
    fail_key   = _MAX_FAIL_KEY.format(username=username)
    await redis.delete(locked_key, fail_key)
    logger.info("[管理解锁] admin_id=%s 解锁账号 username=%s", current_admin["admin_id"], username)
    return success({"message": f"账号 {username} 已解锁"})
