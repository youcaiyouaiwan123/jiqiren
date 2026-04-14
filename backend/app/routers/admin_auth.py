"""管理端认证"""
import logging

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

from app.core.database import get_db
from app.core.security import create_access_token, create_refresh_token, hash_password, verify_password
from app.models.admin import Admin
from app.utils.response import fail, success

router = APIRouter(prefix="/api/admin", tags=["管理端认证"])


class AdminLoginBody(BaseModel):
    username: str
    password: str


@router.post("/login")
async def admin_login(body: AdminLoginBody, db: AsyncSession = Depends(get_db)):
    admin = (await db.execute(select(Admin).where(Admin.username == body.username))).scalar_one_or_none()
    if not admin:
        logger.warning("[管理登录] 账号不存在 | username=%s", body.username)
        return fail(1004, "管理员账号不存在")
    if not verify_password(body.password, admin.password_hash):
        logger.warning("[管理登录] 密码错误 | username=%s", body.username)
        return fail(1001, "密码错误")
    logger.info("[管理登录] 成功 | admin_id=%s username=%s", admin.id, admin.username)
    token_data = {"admin_id": admin.id, "role": "admin", "admin_role": admin.role}
    return success({
        "access_token": create_access_token(token_data),
        "refresh_token": create_refresh_token(token_data),
        "token_type": "bearer",
        "expires_in": 7200,
        "admin": {"id": admin.id, "username": admin.username, "role": admin.role},
    })
