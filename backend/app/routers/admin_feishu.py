"""管理端：飞书路由管理"""
import logging

from fastapi import APIRouter, Depends

logger = logging.getLogger(__name__)
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import PageParams, get_current_admin
from app.models.feishu_route import FeishuRoute
from app.services.feishu_service import _normalize_bitable_ids, inspect_bitable_config
from app.utils.crud import generic_create, generic_delete, generic_list, generic_update
from app.utils.response import fail, success

router = APIRouter(prefix="/api/admin/feishu/routes", tags=["管理端-飞书路由"])


class FeishuRouteBody(BaseModel):
    route_id: int | None = None
    name: str | None = None
    app_id: str | None = None
    app_secret: str | None = None
    app_token: str | None = None
    table_id: str | None = None
    bitable_url: str | None = None
    route_rule: dict | None = None
    is_active: int | None = None


def _normalize_route_payload(data: dict) -> dict:
    payload = dict(data)
    payload.pop("route_id", None)
    bitable_url = str(payload.pop("bitable_url", "") or "").strip()
    app_token = str(payload.get("app_token", "") or "").strip()
    table_id = str(payload.get("table_id", "") or "").strip()

    normalized_app_token, normalized_table_id = _normalize_bitable_ids(
        app_token or bitable_url,
        table_id or bitable_url,
    )
    if normalized_app_token:
        payload["app_token"] = normalized_app_token
    if normalized_table_id:
        payload["table_id"] = normalized_table_id
    return payload


async def _test_route_payload(payload: dict) -> dict:
    if not payload.get("app_id"):
        return fail(1001, "请先填写 App ID")
    if not payload.get("app_secret"):
        return fail(1001, "请先填写 App Secret")
    result = await inspect_bitable_config(
        app_id=str(payload.get("app_id") or ""),
        app_secret=str(payload.get("app_secret") or ""),
        app_token=str(payload.get("app_token") or ""),
        table_id=str(payload.get("table_id") or ""),
    )
    if result.get("ok"):
        return success(result, "连接成功")
    return fail(1001, str(result.get("detail") or "连接失败"), result)


@router.get("")
async def list_routes(admin: dict = Depends(get_current_admin), pager: PageParams = Depends(), db: AsyncSession = Depends(get_db)):
    return await generic_list(db, FeishuRoute, page=pager.page, page_size=pager.page_size, exclude_cols={"app_secret"})


@router.post("")
async def create_route(body: FeishuRouteBody, admin: dict = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    data = _normalize_route_payload(body.model_dump(exclude_none=True))
    if not data.get("app_token") or not data.get("table_id"):
        return fail(1001, "请填写正确的 App Token / Table ID，或直接粘贴完整多维表链接")
    return await generic_create(db, FeishuRoute, data)


@router.post("/test")
async def test_route(body: FeishuRouteBody, admin: dict = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    data = _normalize_route_payload(body.model_dump(exclude_none=True))
    if not data.get("app_secret") and body.route_id:
        row = await db.get(FeishuRoute, body.route_id)
        if row:
            data["app_secret"] = row.app_secret
    return await _test_route_payload(data)


@router.put("/{pk}")
async def update_route(pk: int, body: FeishuRouteBody, admin: dict = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    data = _normalize_route_payload(body.model_dump(exclude_none=True))
    if "app_token" in data and not data.get("app_token"):
        return fail(1001, "请填写正确的 App Token，或直接粘贴完整多维表链接")
    if "table_id" in data and not data.get("table_id"):
        return fail(1001, "请填写正确的 Table ID，或直接粘贴完整多维表链接")
    return await generic_update(db, FeishuRoute, pk, data)


@router.post("/{pk}/test")
async def test_saved_route(pk: int, admin: dict = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    row = await db.get(FeishuRoute, pk)
    if not row:
        return fail(1004, "资源不存在")
    return await _test_route_payload({
        "app_id": row.app_id,
        "app_secret": row.app_secret,
        "app_token": row.app_token,
        "table_id": row.table_id,
    })


@router.delete("/{pk}")
async def delete_route(pk: int, admin: dict = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    return await generic_delete(db, FeishuRoute, pk)
