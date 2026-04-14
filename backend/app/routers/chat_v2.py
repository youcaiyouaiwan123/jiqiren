"""AI 对话：会话列表/新建/历史消息/发送(SSE)"""
import json
import logging
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Depends, UploadFile
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy import delete as sa_delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session, get_db
from app.core.deps import PageParams, get_current_user_id
from app.models.conversation import Conversation
from app.models.message import Message
from app.models.token_usage import TokenUsage
from app.models.user import User
from app.utils.response import fail, paginate, success

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/chat", tags=["AI 对话"])


MAX_AUDIO_SIZE = 25 * 1024 * 1024
ALLOWED_AUDIO_TYPES = {
    "audio/webm",
    "audio/ogg",
    "audio/mp4",
    "audio/mpeg",
    "audio/wav",
    "audio/x-wav",
    "audio/mp3",
    "audio/flac",
    "video/webm",
}

MAX_IMAGE_SIZE = 10 * 1024 * 1024
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp", "image/bmp"}
UPLOAD_DIR = Path(__file__).resolve().parents[2] / "uploads" / "chat_images"


class NewConversationBody(BaseModel):
    title: str | None = None


class RenameConversationBody(BaseModel):
    title: str


class SendMessageBody(BaseModel):
    conversation_id: int | None = None
    message: str
    images: list[dict] | None = None


@router.post("/transcribe")
async def transcribe_audio(
    file: UploadFile,
    user_id: int = Depends(get_current_user_id),
):
    content_type = (file.content_type or "").split(";")[0].strip().lower()
    if content_type not in ALLOWED_AUDIO_TYPES:
        return fail(4001, f"不支持的音频格式: {content_type}")

    audio_bytes = await file.read()
    if len(audio_bytes) > MAX_AUDIO_SIZE:
        return fail(4002, "音频文件过大，请控制在 25MB 以内")
    if len(audio_bytes) < 100:
        return fail(4003, "音频文件过小，请重新录音")

    logger.info("[STT] 收到转写请求 | user_id=%s size=%s type=%s", user_id, len(audio_bytes), content_type)

    try:
        from app.services.stt_service import transcribe_audio as do_transcribe

        text = await do_transcribe(audio_bytes, file.filename or "audio.webm")
    except Exception as exc:
        logger.exception("[STT] 转写失败 | user_id=%s", user_id)
        return fail(5002, f"语音识别失败: {exc}")

    if not text.strip():
        return fail(4004, "未识别到有效语音内容，请重新录音")

    logger.info("[STT] 转写完成 | user_id=%s text_len=%s", user_id, len(text))
    return success({"text": text.strip()})


@router.post("/upload-image")
async def upload_image(
    file: UploadFile,
    user_id: int = Depends(get_current_user_id),
):
    content_type = (file.content_type or "").split(";")[0].strip().lower()
    if content_type not in ALLOWED_IMAGE_TYPES:
        logger.warning("[图片] 格式不支持 | user_id=%s type=%s", user_id, content_type)
        return fail(4001, f"不支持的图片格式: {content_type}")

    image_bytes = await file.read()
    if len(image_bytes) > MAX_IMAGE_SIZE:
        logger.warning("[图片] 文件过大 | user_id=%s size=%s", user_id, len(image_bytes))
        return fail(4002, "图片过大，请控制在 10MB 以内")
    if len(image_bytes) < 100:
        logger.warning("[图片] 文件异常 | user_id=%s size=%s", user_id, len(image_bytes))
        return fail(4003, "图片文件异常")

    ext = Path(file.filename or "image.jpg").suffix.lower()
    if ext not in {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"}:
        ext = ".jpg"

    import uuid

    filename = f"{uuid.uuid4().hex}{ext}"
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    filepath = UPLOAD_DIR / filename
    filepath.write_bytes(image_bytes)

    image_url = f"/api/chat/uploads/{filename}"
    logger.info("[图片] 上传成功 | user_id=%s size=%s url=%s", user_id, len(image_bytes), image_url)
    return success({"url": image_url, "filename": filename, "size": len(image_bytes)})


@router.get("/conversations")
async def list_conversations(
    user_id: int = Depends(get_current_user_id),
    pager: PageParams = Depends(),
    db: AsyncSession = Depends(get_db),
):
    base = select(Conversation).where(Conversation.user_id == user_id)
    total = (await db.execute(select(func.count()).select_from(base.subquery()))).scalar() or 0

    message_stats = (
        select(
            Message.conversation_id.label("conversation_id"),
            func.count(Message.id).label("message_count"),
            func.max(Message.created_at).label("last_message_at"),
        )
        .group_by(Message.conversation_id)
        .subquery()
    )

    rows = (
        await db.execute(
            select(
                Conversation,
                func.coalesce(message_stats.c.message_count, 0).label("message_count"),
                message_stats.c.last_message_at.label("last_message_at"),
            )
            .outerjoin(message_stats, message_stats.c.conversation_id == Conversation.id)
            .where(Conversation.user_id == user_id)
            .order_by(Conversation.updated_at.desc())
            .offset(pager.offset)
            .limit(pager.page_size)
        )
    ).all()

    items = [
        {
            "id": row.Conversation.id,
            "title": row.Conversation.title,
            "message_count": row.message_count,
            "last_message_at": row.last_message_at.isoformat() if row.last_message_at else None,
            "created_at": row.Conversation.created_at.isoformat() if row.Conversation.created_at else None,
            "updated_at": row.Conversation.updated_at.isoformat() if row.Conversation.updated_at else None,
        }
        for row in rows
    ]
    return success(paginate(items, total, pager.page, pager.page_size))


@router.post("/conversations")
async def create_conversation(
    body: NewConversationBody,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    conv = Conversation(user_id=user_id, title=body.title or "新对话")
    db.add(conv)
    await db.flush()
    logger.info("[会话] 新建 | user_id=%s conv_id=%s", user_id, conv.id)
    return success({"id": conv.id, "title": conv.title, "created_at": conv.created_at.isoformat() if conv.created_at else None})


@router.put("/conversations/{conv_id}")
async def rename_conversation(
    conv_id: int,
    body: RenameConversationBody,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    conv = await db.get(Conversation, conv_id)
    if not conv or conv.user_id != user_id:
        return fail(1004, "会话不存在")
    conv.title = body.title.strip()[:200]
    await db.commit()
    logger.info("[会话] 重命名 | user_id=%s conv_id=%s title=%s", user_id, conv_id, conv.title)
    return success({"id": conv.id, "title": conv.title})


@router.delete("/conversations/{conv_id}")
async def delete_conversation(
    conv_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    conv = await db.get(Conversation, conv_id)
    if not conv or conv.user_id != user_id:
        return fail(1004, "会话不存在")

    message_id_subquery = select(Message.id).where(Message.conversation_id == conv_id)
    await db.execute(sa_delete(TokenUsage).where(TokenUsage.message_id.in_(message_id_subquery)))
    await db.execute(sa_delete(Message).where(Message.conversation_id == conv_id))
    await db.delete(conv)
    await db.commit()
    logger.info("[会话] 删除 | user_id=%s conv_id=%s", user_id, conv_id)
    return success(None)


@router.get("/conversations/{conv_id}/messages")
async def get_messages(
    conv_id: int,
    user_id: int = Depends(get_current_user_id),
    pager: PageParams = Depends(),
    db: AsyncSession = Depends(get_db),
):
    conv = await db.get(Conversation, conv_id)
    if not conv or conv.user_id != user_id:
        return fail(1004, "会话不存在")
    base = select(Message).where(Message.conversation_id == conv_id)
    total = (await db.execute(select(func.count()).select_from(base.subquery()))).scalar() or 0
    rows = (
        await db.execute(base.order_by(Message.created_at.asc()).offset(pager.offset).limit(pager.page_size))
    ).scalars().all()
    items = [
        {
            "id": message.id,
            "role": message.role,
            "content": message.content,
            "images": message.images or [],
            "docs": message.docs or [],
            "created_at": message.created_at.isoformat() if message.created_at else None,
        }
        for message in rows
    ]
    return success({"conversation_id": conv_id, **paginate(items, total, pager.page, pager.page_size)})


@router.post("/send")
async def send_message(
    body: SendMessageBody,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    conv = None
    if body.conversation_id:
        conv = await db.get(Conversation, body.conversation_id)
        if not conv or conv.user_id != user_id:
            return fail(1004, "会话不存在")

    user = (
        await db.execute(select(User).where(User.id == user_id).with_for_update())
    ).scalar_one_or_none()
    if not user:
        return fail(1004, "用户不存在")
    if user.status == "banned":
        logger.warning("[对话] 封禁用户尝试发送 | user_id=%s", user_id)
        return fail(2003, "账号已被封禁")

    now = datetime.utcnow()
    has_subscription = (
        user.subscribe_plan != "free"
        and user.subscribe_expire
        and user.subscribe_expire > now
    )
    free_chats_left = user.free_chats_left or 0

    if not has_subscription:
        if free_chats_left <= 0:
            logger.info("[对话] 配额不足 | user_id=%s free_left=%s", user_id, user.free_chats_left)
            return fail(2001, "免费次数已用完，请订阅后继续使用")
        user.free_chats_left = free_chats_left - 1
        free_chats_left = user.free_chats_left

    if conv is None:
        conv = Conversation(user_id=user_id, title=body.message[:50])
        db.add(conv)
        await db.flush()

    conv.updated_at = datetime.utcnow()
    user_msg = Message(
        conversation_id=conv.id,
        user_id=user_id,
        role="user",
        content=body.message,
        images=body.images,
    )
    db.add(user_msg)
    await db.flush()

    logger.info("[对话] 发送 | user_id=%s conv_id=%s msg_len=%s has_sub=%s", user_id, conv.id, len(body.message), has_subscription)
    await db.commit()

    conv_id = conv.id
    user_msg_id = user_msg.id
    subscribe_plan = user.subscribe_plan
    subscribe_expire = user.subscribe_expire.isoformat() if user.subscribe_expire else None

    from app.services.ai_service import stream_ai_response

    async def event_stream():
        full_text = ""
        usage_info = {}
        retrieval_info = {"docs": [], "status": "disabled"}
        try:
            async with async_session() as sse_db:
                async for chunk_text in stream_ai_response(body.message, conv_id, user_id, sse_db, usage_info, retrieval_info):
                    full_text += chunk_text
                    yield f"event: chunk\ndata: {json.dumps({'text': chunk_text}, ensure_ascii=False)}\n\n"

                model_name = usage_info.get("model", "")
                in_tokens = usage_info.get("input_tokens", 0)
                out_tokens = usage_info.get("output_tokens", 0)
                docs = retrieval_info.get("docs", [])

                ai_msg = Message(
                    conversation_id=conv_id,
                    user_id=user_id,
                    role="assistant",
                    content=full_text,
                    docs=docs,
                    input_tokens=in_tokens,
                    output_tokens=out_tokens,
                )
                sse_db.add(ai_msg)
                await sse_db.flush()

                input_price = usage_info.get("input_price", 0.0)
                output_price = usage_info.get("output_price", 0.0)
                cost_usd = round((in_tokens * input_price + out_tokens * output_price) / 1_000_000, 6)
                sse_db.add(
                    TokenUsage(
                        user_id=user_id,
                        message_id=ai_msg.id,
                        model=model_name,
                        input_tokens=in_tokens,
                        output_tokens=out_tokens,
                        cost_usd=cost_usd,
                    )
                )
                await sse_db.execute(
                    update(Conversation)
                    .where(Conversation.id == conv_id)
                    .values(updated_at=datetime.utcnow())
                )

                done_data = {
                    "conversation_id": conv_id,
                    "user_message_id": user_msg_id,
                    "assistant_message_id": ai_msg.id,
                    "text": full_text,
                    "images": [],
                    "docs": docs,
                    "retrieval": retrieval_info,
                    "usage": {
                        "model": model_name,
                        "input_tokens": in_tokens,
                        "output_tokens": out_tokens,
                        "cost_usd": cost_usd,
                    },
                    "quota": {
                        "free_chats_left": free_chats_left,
                        "subscribe_plan": subscribe_plan,
                        "subscribe_expire": subscribe_expire,
                    },
                }
                await sse_db.commit()

                try:
                    from app.services.feishu_sync_runtime import enqueue_chat_sync

                    await enqueue_chat_sync(
                        user_id=user_id,
                        conversation_id=conv_id,
                        user_message_id=user_msg_id,
                        assistant_message_id=ai_msg.id,
                    )
                except Exception:
                    logger.exception("[飞书同步] 入队失败 | user_id=%s conv_id=%s", user_id, conv_id)

                yield f"event: done\ndata: {json.dumps(done_data, ensure_ascii=False)}\n\n"
        except Exception:
            if not has_subscription:
                async with async_session() as rollback_db:
                    await rollback_db.execute(
                        update(User)
                        .where(User.id == user_id)
                        .values(free_chats_left=User.free_chats_left + 1)
                    )
                    await rollback_db.commit()
            logger.exception("[对话] AI响应异常 | user_id=%s conv_id=%s", user_id, conv_id)
            err = {"code": 5001, "message": "AI 暂时繁忙，请稍后重试"}
            yield f"event: error\ndata: {json.dumps(err, ensure_ascii=False)}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
