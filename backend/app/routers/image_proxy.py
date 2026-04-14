"""图片代理：转发飞书附件"""
import logging

import httpx
from fastapi import APIRouter, Depends

logger = logging.getLogger(__name__)
from fastapi.responses import Response

from app.core.deps import get_current_user_id
from app.utils.response import fail

router = APIRouter(prefix="/api/image", tags=["图片代理"])


@router.get("/{file_token}")
async def proxy_image(file_token: str, user_id: int = Depends(get_current_user_id)):
    # TODO: 从 feishu_routes 加载 app_id/app_secret，获取 tenant_access_token
    # 占位实现：返回 404
    return Response(content=b"", status_code=404, media_type="text/plain")
