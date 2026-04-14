import logging
from collections.abc import Mapping
from typing import Any
from urllib.parse import parse_qs, urlparse
import json

import httpx
import redis.asyncio as aioredis

from app.core.redis import get_redis

logger = logging.getLogger(__name__)

FEISHU_OPEN_API = "https://open.feishu.cn/open-apis"
FEISHU_TOKEN_TTL_SECONDS = 115 * 60


class FeishuApiError(Exception):
    pass


def _token_cache_key(app_id: str) -> str:
    return f"feishu:token:{app_id}"


def _format_feishu_error(data: Mapping[str, Any]) -> str:
    code = data.get("code")
    message = data.get("msg") or data.get("message") or "未知错误"
    return f"code={code} msg={message}"


def _mask_identifier(value: str) -> str:
    if len(value) <= 10:
        return value
    return f"{value[:6]}***{value[-4:]}"


def _resolve_redis(redis_client: aioredis.Redis | None = None) -> aioredis.Redis | None:
    return redis_client or get_redis(required=False)


def _extract_app_token(value: str | None) -> str:
    raw = (value or "").strip()
    if not raw:
        return ""
    if "://" in raw:
        parsed = urlparse(raw)
        parts = [part for part in parsed.path.split("/") if part]
        if "base" in parts:
            idx = parts.index("base")
            if idx + 1 < len(parts):
                raw = parts[idx + 1]
        elif "apps" in parts:
            idx = parts.index("apps")
            if idx + 1 < len(parts):
                raw = parts[idx + 1]
        elif parts:
            raw = parts[-1]
    raw = raw.split("?", 1)[0].split("&", 1)[0]
    return raw.strip()


def _extract_table_id(value: str | None) -> str:
    raw = (value or "").strip()
    if not raw:
        return ""
    if "://" in raw:
        parsed = urlparse(raw)
        table_values = parse_qs(parsed.query).get("table")
        if table_values:
            raw = table_values[0]
        else:
            raw = parsed.path.rsplit("/", 1)[-1]
    if "table=" in raw:
        raw = raw.split("table=", 1)[1]
    if "tbl" in raw and not raw.startswith("tbl"):
        raw = raw[raw.index("tbl"):]
    raw = raw.split("?", 1)[0].split("&", 1)[0].split("/", 1)[0]
    return raw.strip()


def _normalize_bitable_ids(app_token: str, table_id: str) -> tuple[str, str]:
    normalized_app_token = _extract_app_token(app_token)
    normalized_table_id = _extract_table_id(table_id)
    if normalized_app_token.startswith("tbl") and normalized_table_id and not normalized_table_id.startswith("tbl"):
        logger.warning(
            "[飞书同步] 检测到 App Token / Table ID 疑似填反，已自动纠正 | app_token=%s table_id=%s",
            _mask_identifier(normalized_app_token),
            _mask_identifier(normalized_table_id),
        )
        normalized_app_token, normalized_table_id = normalized_table_id, normalized_app_token
    return normalized_app_token, normalized_table_id


def _response_detail(response: httpx.Response) -> str:
    text = response.text.strip()
    if not text:
        return f"HTTP {response.status_code}"
    try:
        data = json.loads(text)
        return json.dumps(data, ensure_ascii=False)
    except json.JSONDecodeError:
        return text[:500]


async def inspect_bitable_config(
    *,
    app_id: str,
    app_secret: str,
    app_token: str,
    table_id: str,
    redis_client: aioredis.Redis | None = None,
) -> dict[str, Any]:
    redis_conn = _resolve_redis(redis_client)
    normalized_app_token, normalized_table_id = _normalize_bitable_ids(app_token, table_id)

    if not normalized_app_token:
        return {
            "ok": False,
            "stage": "app_token",
            "detail": "未识别到有效的 App Token，请直接粘贴完整多维表链接或手动填写。",
            "app_token": normalized_app_token,
            "table_id": normalized_table_id,
        }
    if not normalized_table_id:
        return {
            "ok": False,
            "stage": "table_id",
            "detail": "未识别到有效的 Table ID，请直接粘贴完整多维表链接或手动填写。",
            "app_token": normalized_app_token,
            "table_id": normalized_table_id,
        }

    try:
        token = await get_tenant_access_token(app_id, app_secret, redis_conn)
    except FeishuApiError as exc:
        return {
            "ok": False,
            "stage": "tenant_access_token",
            "detail": str(exc),
            "app_token": normalized_app_token,
            "table_id": normalized_table_id,
        }

    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.get(
                f"{FEISHU_OPEN_API}/bitable/v1/apps/{normalized_app_token}/tables",
                headers={"Authorization": f"Bearer {token}"},
                params={"page_size": 200},
            )
            response.raise_for_status()
            data = response.json()
    except httpx.HTTPStatusError as exc:
        detail = _response_detail(exc.response)
        reason = "无法访问该多维表应用，请检查 App Token 是否正确，或确认飞书应用已获得该多维表访问权限。"
        if "403" in detail or "PERMISSION" in detail.upper():
            reason = "当前飞书应用缺少多维表访问权限，请检查应用权限与文档授权。"
        return {
            "ok": False,
            "stage": "app_token_access",
            "detail": reason,
            "raw_detail": detail,
            "app_token": normalized_app_token,
            "table_id": normalized_table_id,
        }

    if data.get("code") != 0:
        detail = _format_feishu_error(data)
        reason = "读取多维表列表失败，请检查 App Token 或应用权限。"
        if str(data.get("msg") or "").upper() == "NOTEXIST":
            reason = "找不到该多维表应用，请检查 App Token 是否正确。"
        return {
            "ok": False,
            "stage": "app_token_access",
            "detail": reason,
            "raw_detail": detail,
            "app_token": normalized_app_token,
            "table_id": normalized_table_id,
        }

    items = ((data.get("data") or {}).get("items") or [])
    matched = None
    for item in items:
        if str(item.get("table_id") or "") == normalized_table_id:
            matched = item
            break

    if not matched:
        candidates = [
            {
                "name": str(item.get("name") or ""),
                "table_id": str(item.get("table_id") or ""),
            }
            for item in items[:5]
        ]
        return {
            "ok": False,
            "stage": "table_id",
            "detail": "已成功连接到多维表应用，但未找到目标 Table ID，请检查表链接是否来自同一个 Base。",
            "app_token": normalized_app_token,
            "table_id": normalized_table_id,
            "table_count": len(items),
            "candidates": candidates,
        }

    return {
        "ok": True,
        "stage": "done",
        "detail": "连接成功，当前飞书应用可以访问目标多维表。",
        "app_token": normalized_app_token,
        "table_id": normalized_table_id,
        "table_name": str(matched.get("name") or ""),
        "table_count": len(items),
    }


async def list_bitable_fields(
    *,
    app_id: str,
    app_secret: str,
    app_token: str,
    table_id: str,
    redis_client: aioredis.Redis | None = None,
) -> list[dict[str, Any]]:
    redis_conn = _resolve_redis(redis_client)
    normalized_app_token, normalized_table_id = _normalize_bitable_ids(app_token, table_id)
    last_error: Exception | None = None

    for force_refresh in (False, True):
        try:
            token = await get_tenant_access_token(
                app_id,
                app_secret,
                redis_conn,
                force_refresh=force_refresh,
            )
            async with httpx.AsyncClient(timeout=20.0) as client:
                response = await client.get(
                    f"{FEISHU_OPEN_API}/bitable/v1/apps/{normalized_app_token}/tables/{normalized_table_id}/fields",
                    headers={"Authorization": f"Bearer {token}"},
                    params={"page_size": 200},
                )
                response.raise_for_status()
                data = response.json()
            if data.get("code") == 0:
                return list(((data.get("data") or {}).get("items") or []))
            last_error = FeishuApiError(f"读取飞书多维表字段失败: {_format_feishu_error(data)}")
            if redis_conn:
                await redis_conn.delete(_token_cache_key(app_id))
        except httpx.HTTPStatusError as exc:
            detail = _response_detail(exc.response)
            last_error = FeishuApiError(f"调用飞书接口异常: status={exc.response.status_code} detail={detail}")
            if not force_refresh:
                if redis_conn:
                    await redis_conn.delete(_token_cache_key(app_id))
                continue
            break
        except Exception as exc:
            last_error = exc
            if not force_refresh:
                if redis_conn:
                    await redis_conn.delete(_token_cache_key(app_id))
                continue
            break

    if isinstance(last_error, FeishuApiError):
        raise last_error
    if last_error is not None:
        raise FeishuApiError(f"调用飞书接口异常: {last_error}") from last_error
    raise FeishuApiError("调用飞书接口异常")


async def get_tenant_access_token(
    app_id: str,
    app_secret: str,
    redis_client: aioredis.Redis | None = None,
    *,
    force_refresh: bool = False,
) -> str:
    redis_conn = _resolve_redis(redis_client)
    cache_key = _token_cache_key(app_id)
    if redis_conn is not None and not force_refresh:
        cached = await redis_conn.get(cache_key)
        if cached:
            return cached

    async with httpx.AsyncClient(timeout=20.0) as client:
        response = await client.post(
            f"{FEISHU_OPEN_API}/auth/v3/tenant_access_token/internal",
            json={"app_id": app_id, "app_secret": app_secret},
        )
        response.raise_for_status()
        data = response.json()

    if data.get("code") != 0 or not data.get("tenant_access_token"):
        raise FeishuApiError(f"获取飞书 tenant_access_token 失败: {_format_feishu_error(data)}")

    token = data["tenant_access_token"]
    expire_seconds = int(data.get("expire", FEISHU_TOKEN_TTL_SECONDS))
    ttl_seconds = max(60, min(FEISHU_TOKEN_TTL_SECONDS, expire_seconds - 300))
    if redis_conn is not None:
        await redis_conn.set(cache_key, token, ex=ttl_seconds)
    return token


async def create_bitable_record(
    *,
    app_id: str,
    app_secret: str,
    app_token: str,
    table_id: str,
    fields: Mapping[str, Any],
    redis_client: aioredis.Redis | None = None,
) -> dict[str, Any]:
    redis_conn = _resolve_redis(redis_client)
    last_error: Exception | None = None
    payload_fields = {k: v for k, v in fields.items() if v is not None}
    normalized_app_token, normalized_table_id = _normalize_bitable_ids(app_token, table_id)

    for force_refresh in (False, True):
        try:
            token = await get_tenant_access_token(
                app_id,
                app_secret,
                redis_conn,
                force_refresh=force_refresh,
            )
            async with httpx.AsyncClient(timeout=20.0) as client:
                response = await client.post(
                    f"{FEISHU_OPEN_API}/bitable/v1/apps/{normalized_app_token}/tables/{normalized_table_id}/records",
                    headers={"Authorization": f"Bearer {token}"},
                    json={"fields": payload_fields},
                )
                response.raise_for_status()
                data = response.json()
            if data.get("code") == 0:
                return data.get("data") or {}
            last_error = FeishuApiError(f"写入飞书多维表格失败: {_format_feishu_error(data)}")
            if redis_conn:
                await redis_conn.delete(_token_cache_key(app_id))
        except httpx.HTTPStatusError as exc:
            response_text = exc.response.text.strip()
            detail = response_text[:500] if response_text else str(exc)
            last_error = FeishuApiError(f"调用飞书接口异常: status={exc.response.status_code} detail={detail}")
            if not force_refresh:
                if redis_conn:
                    await redis_conn.delete(_token_cache_key(app_id))
                continue
            break
        except Exception as exc:
            last_error = exc
            if not force_refresh:
                if redis_conn:
                    await redis_conn.delete(_token_cache_key(app_id))
                continue
            break

    if isinstance(last_error, FeishuApiError):
        raise last_error
    if last_error is not None:
        raise FeishuApiError(f"调用飞书接口异常: {last_error}") from last_error
    raise FeishuApiError("调用飞书接口异常")
