import asyncio
import json
import logging
import time
from typing import Any

from sqlalchemy import select

from app.core.database import async_session
from app.core.redis import get_redis
from app.models.conversation import Conversation
from app.models.feishu_route import FeishuRoute
from app.models.message import Message
from app.models.token_usage import TokenUsage
from app.models.user import User
from app.services.feishu_service import FeishuApiError, create_bitable_record, list_bitable_fields

logger = logging.getLogger(__name__)

STREAM_KEY = "feishu:sync:stream"
DELAYED_KEY = "feishu:sync:delayed"
GROUP_NAME = "feishu:sync"
CONSUMER_NAME = "worker"
DONE_KEY_PREFIX = "feishu:sync:done:"
LOCK_KEY_PREFIX = "feishu:sync:lock:"
DONE_TTL_SECONDS = 90 * 24 * 3600
LOCK_TTL_SECONDS = 5 * 60
REQUEUE_BATCH_SIZE = 20
RETRY_DELAYS = (1, 5, 30)
DEFAULT_SYNC_TYPE = "conversation_record"

_worker_task: asyncio.Task | None = None
_stop_event: asyncio.Event | None = None


def _route_sync_type(route_rule: Any) -> str:
    if isinstance(route_rule, dict):
        sync_type = str(route_rule.get("sync_type") or "").strip().lower()
        if sync_type:
            return sync_type
    return DEFAULT_SYNC_TYPE


def _json_text(value: Any) -> str:
    if value in (None, "", [], {}):
        return ""
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False)


def _image_text(value: Any) -> str:
    if not value:
        return ""
    if isinstance(value, list):
        items: list[str] = []
        for item in value:
            if isinstance(item, dict):
                text = item.get("url") or item.get("tmp_url") or item.get("file_token") or item.get("name")
                if text:
                    items.append(str(text))
            elif item:
                items.append(str(item))
        if items:
            return "\n".join(items)
    return _json_text(value)


def _dt_text(value: Any) -> str:
    if value is None:
        return ""
    if hasattr(value, "strftime"):
        return value.strftime("%Y-%m-%d %H:%M:%S")
    return str(value)


def _fallback_text_field(field_defs: list[dict[str, Any]]) -> str | None:
    preferred_names = ("文本", "内容", "记录", "标题")
    for preferred_name in preferred_names:
        for field in field_defs:
            if str(field.get("field_name") or "") == preferred_name:
                return preferred_name
    for field in field_defs:
        if field.get("is_primary") and int(field.get("type") or 0) == 1:
            field_name = str(field.get("field_name") or "")
            if field_name:
                return field_name
    for field in field_defs:
        if int(field.get("type") or 0) == 1:
            field_name = str(field.get("field_name") or "")
            if field_name:
                return field_name
    return None


def _conversation_text_payload(fields: dict[str, Any]) -> str:
    lines: list[str] = []
    for key, value in fields.items():
        if value in (None, "", [], {}):
            continue
        lines.append(f"{key}: {value}")
    return "\n".join(lines)


def _job_done_key(job: dict[str, Any]) -> str:
    return f"{DONE_KEY_PREFIX}{int(job['assistant_message_id'])}"


def _job_lock_key(job: dict[str, Any]) -> str:
    return f"{LOCK_KEY_PREFIX}{int(job['assistant_message_id'])}"


def _encode_job(job: dict[str, Any]) -> str:
    return json.dumps(job, ensure_ascii=False)


def _decode_job(payload: str) -> dict[str, Any]:
    return json.loads(payload)


async def _ensure_stream_group(redis) -> None:
    try:
        await redis.xgroup_create(STREAM_KEY, GROUP_NAME, id="0-0", mkstream=True)
    except Exception as exc:
        if "BUSYGROUP" not in str(exc):
            raise


async def _ack_stream_entry(redis, entry_id: str) -> None:
    pipe = redis.pipeline(transaction=True)
    pipe.xack(STREAM_KEY, GROUP_NAME, entry_id)
    pipe.xdel(STREAM_KEY, entry_id)
    await pipe.execute()


async def _schedule_retry(redis, job: dict[str, Any], delay: int) -> None:
    await redis.zadd(DELAYED_KEY, {_encode_job(job): time.time() + delay})


async def _requeue_due_jobs(redis) -> None:
    due_payloads = await redis.zrangebyscore(
        DELAYED_KEY,
        min=0,
        max=time.time(),
        start=0,
        num=REQUEUE_BATCH_SIZE,
    )
    for payload in due_payloads:
        pipe = redis.pipeline(transaction=True)
        pipe.xadd(STREAM_KEY, {"payload": payload})
        pipe.zrem(DELAYED_KEY, payload)
        await pipe.execute()


def _extract_stream_job(stream_data: list) -> tuple[str, dict[str, Any]] | None:
    if not stream_data:
        return None
    _, entries = stream_data[0]
    if not entries:
        return None
    entry_id, fields = entries[0]
    payload = fields.get("payload")
    if not payload:
        return None
    return entry_id, _decode_job(payload)


async def _read_next_stream_job(redis) -> tuple[str, dict[str, Any]] | None:
    pending = await redis.xreadgroup(GROUP_NAME, CONSUMER_NAME, {STREAM_KEY: "0"}, count=1)
    job = _extract_stream_job(pending)
    if job:
        return job
    fresh = await redis.xreadgroup(GROUP_NAME, CONSUMER_NAME, {STREAM_KEY: ">"}, count=1, block=1000)
    return _extract_stream_job(fresh)


async def _resolve_record_fields(route: FeishuRoute, fields: dict[str, Any]) -> dict[str, Any]:
    field_defs = await list_bitable_fields(
        app_id=route.app_id,
        app_secret=route.app_secret,
        app_token=route.app_token,
        table_id=route.table_id,
    )
    field_names = {
        str(field.get("field_name") or "")
        for field in field_defs
        if field.get("field_name")
    }
    if field_names and all(key in field_names for key in fields):
        return fields

    fallback_field = _fallback_text_field(field_defs)
    if fallback_field:
        logger.info(
            "[Feishu Sync] field mismatch, falling back to single text field | table_id=%s field=%s",
            route.table_id,
            fallback_field,
        )
        return {fallback_field: _conversation_text_payload(fields)}

    missing_fields = [key for key in fields if key not in field_names][:5]
    raise FeishuApiError(f"目标飞书表字段不匹配，缺少字段: {', '.join(missing_fields)}")


async def enqueue_chat_sync(*, user_id: int, conversation_id: int, user_message_id: int, assistant_message_id: int) -> None:
    redis = get_redis(required=False)
    if redis is None:
        logger.warning("[Feishu Sync] Redis unavailable, skipping enqueue | ai_msg_id=%s", assistant_message_id)
        return
    payload = {
        "job_type": DEFAULT_SYNC_TYPE,
        "attempt": 0,
        "user_id": user_id,
        "conversation_id": conversation_id,
        "user_message_id": user_message_id,
        "assistant_message_id": assistant_message_id,
    }
    await redis.xadd(STREAM_KEY, {"payload": _encode_job(payload)})


async def start_feishu_sync_worker() -> None:
    global _worker_task, _stop_event
    if _worker_task and not _worker_task.done():
        return
    redis = get_redis(required=False)
    if redis is None:
        logger.warning("[Feishu Sync] Redis unavailable, worker not started")
        return
    await _ensure_stream_group(redis)
    _stop_event = asyncio.Event()
    _worker_task = asyncio.create_task(_worker_loop())
    logger.info("[Feishu Sync] worker started")


async def stop_feishu_sync_worker() -> None:
    global _worker_task, _stop_event
    if _stop_event:
        _stop_event.set()
    if _worker_task:
        try:
            await _worker_task
        except asyncio.CancelledError:
            pass
    _worker_task = None
    _stop_event = None
    logger.info("[Feishu Sync] worker stopped")


async def _worker_loop() -> None:
    redis = get_redis(required=False)
    if redis is None:
        logger.warning("[Feishu Sync] Redis unavailable, worker exiting")
        return
    while _stop_event and not _stop_event.is_set():
        try:
            await _requeue_due_jobs(redis)
            item = await _read_next_stream_job(redis)
            if not item:
                continue
            entry_id, job = item
            await _process_stream_message(redis, entry_id, job)
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("[Feishu Sync] worker loop failed")
            await asyncio.sleep(1)


async def _process_stream_message(redis, entry_id: str, job: dict[str, Any]) -> None:
    try:
        await _process_job(job)
    except Exception as exc:
        attempt = int(job.get("attempt") or 0)
        if attempt < len(RETRY_DELAYS):
            delay = RETRY_DELAYS[attempt]
            next_job = {**job, "attempt": attempt + 1}
            logger.warning(
                "[Feishu Sync] job failed, scheduling retry | delay=%ss attempt=%s ai_msg_id=%s err=%s",
                delay,
                attempt + 1,
                job.get("assistant_message_id"),
                exc,
            )
            await _schedule_retry(redis, next_job, delay)
        else:
            logger.exception("[Feishu Sync] job exhausted retries | job=%s", job)
    finally:
        await _ack_stream_entry(redis, entry_id)


async def _process_job(job: dict[str, Any]) -> None:
    redis = get_redis(required=False)
    if redis is None:
        raise RuntimeError("Redis unavailable")
    lock_key = _job_lock_key(job)
    locked = await redis.set(lock_key, "1", nx=True, ex=LOCK_TTL_SECONDS)
    if not locked:
        raise RuntimeError(f"job locked: {job.get('assistant_message_id')}")
    try:
        job_type = str(job.get("job_type") or DEFAULT_SYNC_TYPE)
        if job_type == DEFAULT_SYNC_TYPE:
            await _sync_conversation_record(job)
            return
        logger.warning("[Feishu Sync] unknown job type: %s", job_type)
    finally:
        await redis.delete(lock_key)


async def _select_route(sync_type: str) -> FeishuRoute | None:
    async with async_session() as db:
        routes = (
            await db.execute(
                select(FeishuRoute)
                .where(FeishuRoute.is_active == 1)
                .order_by(FeishuRoute.id.asc())
            )
        ).scalars().all()
    if not routes:
        return None
    for route in routes:
        if _route_sync_type(route.route_rule) == sync_type:
            return route
    if sync_type == DEFAULT_SYNC_TYPE:
        return routes[0]
    return None


async def _sync_conversation_record(job: dict[str, Any]) -> None:
    route = await _select_route(DEFAULT_SYNC_TYPE)
    if not route:
        logger.info("[Feishu Sync] no active route configured, skipping")
        return

    redis = get_redis(required=False)
    done_key = _job_done_key(job)
    async with async_session() as db:
        user = await db.get(User, int(job["user_id"]))
        conversation = await db.get(Conversation, int(job["conversation_id"]))
        user_msg = await db.get(Message, int(job["user_message_id"]))
        assistant_msg = await db.get(Message, int(job["assistant_message_id"]))
        token_usage = (
            await db.execute(
                select(TokenUsage)
                .where(TokenUsage.message_id == int(job["assistant_message_id"]))
                .order_by(TokenUsage.id.desc())
                .limit(1)
            )
        ).scalar_one_or_none()

        if not user or not conversation or not user_msg or not assistant_msg:
            logger.warning("[Feishu Sync] dependent records missing, skipping | job=%s", job)
            return

        if user_msg.feishu_synced and assistant_msg.feishu_synced:
            if redis is not None:
                await redis.set(done_key, "1", ex=DONE_TTL_SECONDS)
            logger.info("[Feishu Sync] message already marked synced | ai_msg_id=%s", assistant_msg.id)
            return

        if redis is not None and await redis.get(done_key):
            user_msg.feishu_synced = 1
            assistant_msg.feishu_synced = 1
            await db.commit()
            logger.info("[Feishu Sync] recovered local sync state from idempotency key | ai_msg_id=%s", assistant_msg.id)
            return

        fields = {
            "用户ID": str(user.id),
            "昵称": user.nickname or "",
            "手机号": user.phone or "",
            "邮箱": user.email or "",
            "订阅计划": user.subscribe_plan or "",
            "剩余免费次数": user.free_chats_left,
            "会话ID": str(conversation.id),
            "用户消息ID": str(user_msg.id),
            "AI消息ID": str(assistant_msg.id),
            "用户问题": user_msg.content,
            "用户截图": _image_text(user_msg.images),
            "AI回复": assistant_msg.content,
            "推荐文档": _json_text(assistant_msg.docs),
            "模型": token_usage.model if token_usage and token_usage.model else "",
            "输入Token": token_usage.input_tokens if token_usage else 0,
            "输出Token": token_usage.output_tokens if token_usage else 0,
            "费用USD": float(token_usage.cost_usd or 0) if token_usage and token_usage.cost_usd is not None else 0,
            "创建时间": _dt_text(assistant_msg.created_at or user_msg.created_at),
        }
        write_fields = await _resolve_record_fields(route, fields)

        result = await create_bitable_record(
            app_id=route.app_id,
            app_secret=route.app_secret,
            app_token=route.app_token,
            table_id=route.table_id,
            fields=write_fields,
        )

        record_id = ((result.get("record") or {}).get("record_id") if isinstance(result, dict) else None)
        if redis is not None:
            await redis.set(done_key, str(record_id or "1"), ex=DONE_TTL_SECONDS)
        user_msg.feishu_synced = 1
        assistant_msg.feishu_synced = 1
        await db.commit()
        logger.info(
            "[Feishu Sync] completed | conv_id=%s user_msg_id=%s ai_msg_id=%s record_id=%s",
            conversation.id,
            user_msg.id,
            assistant_msg.id,
            record_id,
        )
