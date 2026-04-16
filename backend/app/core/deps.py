"""公共依赖注入"""
from fastapi import Depends, Header, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import decode_token
from app.models.user import User
from app.utils.response import fail


class BizException(Exception):
    """业务异常，携带 code + message，由 exception_handler 统一返回 JSON"""
    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message


async def get_current_user_id(db: AsyncSession = Depends(get_db), authorization: str = Header(None)) -> int:
    """从 JWT 提取当前用户 ID"""
    if not authorization or not authorization.startswith("Bearer "):
        raise BizException(1002, "未登录")
    token = authorization.split(" ", 1)[1]
    payload = decode_token(token)
    if not payload or payload.get("type") != "access":
        raise BizException(1002, "Token 无效或已过期")
    user_id = payload.get("user_id")
    if not user_id:
        raise BizException(1002, "Token 无效")
    user_id_int = int(user_id)
    user = await db.get(User, user_id_int)
    if not user or user.deleted_at is not None:
        raise BizException(1002, "账号不存在或已注销")
    if user.status == "banned":
        raise BizException(1002, "账号已被封禁")
    return user_id_int


async def get_current_admin(authorization: str = Header(None)) -> dict:
    """从 JWT 提取当前管理员信息"""
    if not authorization or not authorization.startswith("Bearer "):
        raise BizException(1002, "未登录")
    token = authorization.split(" ", 1)[1]
    payload = decode_token(token)
    if not payload or payload.get("type") != "access" or payload.get("role") != "admin":
        raise BizException(1003, "权限不足")
    return {"admin_id": int(payload["admin_id"]), "role": payload.get("admin_role", "normal")}


class PageParams:
    def __init__(self, page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=200)):
        self.page = page
        self.page_size = page_size

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size
