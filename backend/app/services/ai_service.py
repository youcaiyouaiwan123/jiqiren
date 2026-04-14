"""AI 服务：调用大模型 streaming，支持 Anthropic / OpenAI / Google / 智谱"""
import base64
import logging
import mimetypes
import re
from pathlib import Path
from typing import Any, AsyncGenerator
from urllib.parse import urlsplit, urlunsplit

from app.config import get_settings
from app.services.embedding_service import embed_texts
from app.services.knowledge_config_service import build_effective_knowledge_config, load_knowledge_config_map
from app.services.knowledge_index import query_knowledge
from app.services.knowledge_loader import load_knowledge_chunks
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ai_config import AiConfig
from app.models.llm_provider import LlmProvider
from app.models.message import Message

logger = logging.getLogger(__name__)
settings = get_settings()

_PROVIDER_ALIASES = {
    "anthropic": "claude",
    "claude": "claude",
    "openai": "openai",
    "gpt": "openai",
    "google": "gemini",
    "gemini": "gemini",
    "zhipu": "zhipu",
    "glm": "zhipu",
}

_PROVIDER_ENDPOINT_SUFFIXES = {
    "claude": ("/v1/messages",),
    "openai": ("/v1/chat/completions", "/chat/completions"),
    "gemini": ("/v1beta/models", "/v1/models", "/models"),
    "zhipu": ("/api/paas/v4/chat/completions", "/v4/chat/completions", "/chat/completions"),
}

_PROVIDER_DEFAULT_BASE_PATHS = {
    "openai": "/v1",
    "zhipu": "/api/paas/v4",
}


def _normalize_provider(provider: str | None) -> str:
    key = (provider or "").strip().lower()
    return _PROVIDER_ALIASES.get(key, key)


def _normalize_api_base(provider: str, api_url: str | None) -> str | None:
    raw = (api_url or "").strip()
    if not raw:
        return None
    if "://" not in raw:
        return raw.rstrip("/")
    parts = urlsplit(raw)
    path = parts.path.rstrip("/")
    for suffix in _PROVIDER_ENDPOINT_SUFFIXES.get(provider, ()): 
        if path.endswith(suffix):
            path = path[:-len(suffix)]
            break
    if path in ("", "/") and provider in _PROVIDER_DEFAULT_BASE_PATHS:
        path = _PROVIDER_DEFAULT_BASE_PATHS[provider]
    return urlunsplit((parts.scheme, parts.netloc, path, "", ""))


def _parse_float(value: str | None, default: float) -> float:
    try:
        return float(value) if value is not None else default
    except (TypeError, ValueError):
        return default


def _parse_int(value: str | None, default: int) -> int:
    try:
        return max(1, int(value)) if value is not None else default
    except (TypeError, ValueError):
        return default


def _parse_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def _build_doc_snippet(content: str, limit: int = 160) -> str:
    text = " ".join(content.split())
    if len(text) <= limit:
        return text
    return text[: limit - 3].rstrip() + "..."


def _short_error_text(exc: Exception, limit: int = 240) -> str:
    text = " ".join(str(exc).split()) or exc.__class__.__name__
    if len(text) <= limit:
        return text
    return text[: limit - 3].rstrip() + "..."


def _normalize_search_text(value: str) -> str:
    return re.sub(r"\s+", "", (value or "").strip().lower())


def _search_terms(text: str) -> list[str]:
    normalized = _normalize_search_text(text)
    if not normalized:
        return []
    terms: list[str] = []
    for part in re.split(r"[^\w\u4e00-\u9fff]+", normalized):
        if part and part not in terms:
            terms.append(part)
    for size in (4, 3, 2):
        if len(normalized) < size:
            continue
        for index in range(len(normalized) - size + 1):
            term = normalized[index:index + size]
            if term not in terms:
                terms.append(term)
    for char in normalized:
        if char not in terms:
            terms.append(char)
    return terms


def _keyword_match_score(message: str, item: dict[str, Any]) -> float:
    query = _normalize_search_text(message)
    if not query:
        return 0.0
    title = _normalize_search_text(str(item.get("title") or ""))
    source_title = _normalize_search_text(str(item.get("source_title") or ""))
    aliases = _normalize_search_text("".join(str(alias) for alias in (item.get("aliases") or [])))
    tags = _normalize_search_text("".join(str(tag) for tag in (item.get("tags") or [])))
    content = _normalize_search_text(str(item.get("content") or ""))
    title_zone = f"{title}{source_title}{aliases}"
    body_zone = f"{tags}{content}"
    if query in title_zone:
        return 0.99
    if query in body_zone:
        return 0.95
    weighted_hits = 0.0
    weighted_total = 0.0
    for term in _search_terms(message):
        if not term:
            continue
        base_weight = 1.6 if len(term) >= 4 else 1.3 if len(term) == 3 else 1.0 if len(term) == 2 else 0.35
        weighted_total += base_weight
        if term in title_zone:
            weighted_hits += base_weight * 1.4
        elif term in tags:
            weighted_hits += base_weight * 1.05
        elif term in body_zone:
            weighted_hits += base_weight * 0.85
    if weighted_total <= 0:
        return 0.0
    return round(min(0.97, weighted_hits / (weighted_total * 1.4)), 4)


def _fallback_keyword_matches(message: str, vault_path: str, top_k: int, min_score: float) -> list[dict[str, Any]]:
    chunks, _ = load_knowledge_chunks(vault_path)
    threshold = min(0.6, max(0.25, min_score * 0.8))
    matches: list[dict[str, Any]] = []
    for item in chunks:
        score = _keyword_match_score(message, item)
        if score < threshold:
            continue
        matches.append(
            {
                "title": item.get("title") or item.get("source_title") or "未命名知识",
                "source": item.get("source_file") or "",
                "source_title": item.get("source_title") or "",
                "tags": item.get("tags") or [],
                "content": item.get("content") or "",
                "score": score,
            }
        )
    matches.sort(key=lambda row: (row.get("score", 0), len(str(row.get("title") or "")), len(str(row.get("content") or ""))), reverse=True)
    return matches[: max(1, top_k)]


# ──────────────────── 辅助：图片多模态 ────────────────────

_UPLOADS_DIR = Path(__file__).resolve().parents[2] / "uploads" / "chat_images"


def _image_to_base64(image_info: dict) -> tuple[str, str] | None:
    """将图片信息转为 (base64_data, media_type)，失败返回 None。"""
    url = image_info.get("url", "")
    if not url:
        return None
    # 本地上传的图片：/api/chat/uploads/xxx.jpg
    if url.startswith("/api/chat/uploads/"):
        filename = url.split("/")[-1]
        filepath = _UPLOADS_DIR / filename
        if not filepath.exists():
            logger.warning("[多模态] 图片文件不存在: %s", filepath)
            return None
        data = filepath.read_bytes()
        mime = mimetypes.guess_type(filename)[0] or "image/jpeg"
        return base64.b64encode(data).decode("utf-8"), mime
    return None


def _build_openai_messages(history: list[dict]) -> list[dict]:
    """构建 OpenAI / 智谱格式的多模态消息（content 为 list）。"""
    result = []
    for msg in history:
        images = msg.get("images") or []
        if msg["role"] == "user" and images:
            content_parts: list[dict] = []
            for img in images:
                b64 = _image_to_base64(img)
                if b64:
                    content_parts.append({
                        "type": "image_url",
                        "image_url": {"url": f"data:{b64[1]};base64,{b64[0]}"},
                    })
            content_parts.append({"type": "text", "text": msg["content"]})
            result.append({"role": "user", "content": content_parts})
        else:
            result.append({"role": msg["role"], "content": msg["content"]})
    return result


def _build_anthropic_messages(history: list[dict]) -> list[dict]:
    """构建 Anthropic Claude 格式的多模态消息。"""
    result = []
    for msg in history:
        images = msg.get("images") or []
        if msg["role"] == "user" and images:
            content_parts: list[dict] = []
            for img in images:
                b64 = _image_to_base64(img)
                if b64:
                    content_parts.append({
                        "type": "image",
                        "source": {"type": "base64", "media_type": b64[1], "data": b64[0]},
                    })
            content_parts.append({"type": "text", "text": msg["content"]})
            result.append({"role": "user", "content": content_parts})
        else:
            result.append({"role": msg["role"], "content": msg["content"]})
    return result


def _build_google_contents(history: list[dict]) -> list[dict]:
    """构建 Google Gemini 格式的多模态内容。"""
    contents = []
    for msg in history:
        role = "model" if msg["role"] == "assistant" else "user"
        images = msg.get("images") or []
        parts: list[dict] = []
        if role == "user" and images:
            for img in images:
                b64 = _image_to_base64(img)
                if b64:
                    parts.append({"inline_data": {"mime_type": b64[1], "data": b64[0]}})
        parts.append({"text": msg["content"]})
        contents.append({"role": role, "parts": parts})
    return contents


# ──────────────────── 辅助：加载配置 ────────────────────


async def _load_ai_config(db: AsyncSession) -> dict[str, str]:
    rows = (await db.execute(select(AiConfig))).scalars().all()
    return {r.config_key: r.config_value for r in rows}


async def _load_default_provider(db: AsyncSession) -> LlmProvider | None:
    return (
        await db.execute(
            select(LlmProvider)
            .where(LlmProvider.is_active == 1, LlmProvider.is_default == 1)
            .order_by(LlmProvider.id.desc())
            .limit(1)
        )
    ).scalar_one_or_none()


async def _load_active_providers(db: AsyncSession) -> list[LlmProvider]:
    """加载所有启用的模型，is_default=1 排最前面。"""
    rows = (
        await db.execute(
            select(LlmProvider)
            .where(LlmProvider.is_active == 1)
            .order_by(LlmProvider.is_default.desc(), LlmProvider.id.desc())
        )
    ).scalars().all()
    return list(rows)


async def _load_history(db: AsyncSession, conversation_id: int, limit: int = 20) -> list[dict]:
    """加载最近 N 条消息（含刚提交的用户消息），按时间正序返回。"""
    rows = (
        await db.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc())
            .limit(limit)
        )
    ).scalars().all()
    return [
        {"role": m.role, "content": m.content, "images": m.images or []}
        for m in reversed(rows)
    ]


async def _retrieve_knowledge_docs(
    message: str,
    ai_cfg: dict[str, str],
    db: AsyncSession,
) -> tuple[str, list[dict], dict[str, Any]]:
    if not _parse_bool(ai_cfg.get("knowledge_enabled"), False):
        return "", [], {"enabled": False, "status": "disabled", "docs": [], "message": "知识库检索未开启"}

    provider_name = (ai_cfg.get("knowledge_embedding_provider") or settings.KNOWLEDGE_EMBEDDING_PROVIDER).strip()
    model_name = (ai_cfg.get("knowledge_embedding_model") or settings.KNOWLEDGE_EMBEDDING_MODEL).strip() or None
    top_k = _parse_int(ai_cfg.get("knowledge_top_k"), 3)
    min_score = _parse_float(ai_cfg.get("knowledge_min_score"), 0.35)
    knowledge_cfg = await load_knowledge_config_map(db)
    runtime_cfg = build_effective_knowledge_config(knowledge_cfg)
    embedding_meta: dict[str, Any] = {}
    retrieval_state: dict[str, Any] = {
        "enabled": True,
        "status": "miss",
        "mode": "vector",
        "provider": provider_name,
        "model": model_name or "",
        "base_url": "",
        "top_k": top_k,
        "min_score": min_score,
        "docs": [],
        "message": "未命中知识库",
    }

    try:
        vectors = await embed_texts(db, [message], provider_name=provider_name, model_name=model_name, runtime_meta=embedding_meta)
        retrieval_state["provider"] = embedding_meta.get("provider") or retrieval_state["provider"]
        retrieval_state["model"] = embedding_meta.get("model") or retrieval_state["model"]
        retrieval_state["base_url"] = embedding_meta.get("base_url") or ""
        if not vectors:
            retrieval_state["status"] = "failed"
            retrieval_state["message"] = "知识库 embedding 返回为空，本次回答未参考知识库"
            return "", [], retrieval_state
        matches = query_knowledge(runtime_cfg["index_dir"], vectors[0], top_k=top_k)
    except Exception as exc:
        retrieval_state["status"] = "failed"
        retrieval_state["error"] = _short_error_text(exc)
        retrieval_state["message"] = "知识库检索失败，本次回答未参考知识库"
        logger.exception("[知识库] 检索失败 | provider=%s model=%s", provider_name, model_name or "default")
        fallback_hits = _fallback_keyword_matches(message, runtime_cfg["vault_path"], top_k=top_k, min_score=min_score)
        if not fallback_hits:
            return "", [], retrieval_state
        matches = fallback_hits
        retrieval_state["status"] = "success"
        retrieval_state["mode"] = "keyword_fallback"
        retrieval_state["message"] = f"Embedding 服务异常，已切换到关键词检索并命中 {len(fallback_hits)} 条知识"
        logger.warning("[知识库] Embedding 异常，已切换关键词检索 | hits=%s error=%s", len(fallback_hits), retrieval_state.get("error"))

    hits = [item for item in matches if item.get("score", 0) >= min_score]
    if not hits:
        fallback_hits = _fallback_keyword_matches(message, runtime_cfg["vault_path"], top_k=top_k, min_score=min_score)
        if not fallback_hits:
            retrieval_state["status"] = "miss"
            retrieval_state["message"] = "本次未命中知识库，当前回答主要基于通用模型"
            logger.info("[知识库] 未命中有效知识 | top_k=%s min_score=%s", top_k, min_score)
            return "", [], retrieval_state
        hits = fallback_hits
        retrieval_state["mode"] = "keyword_fallback"
        retrieval_state["message"] = f"向量检索未命中，已通过关键词检索命中 {len(fallback_hits)} 条知识"
        logger.info("[知识库] 向量未命中，关键词检索命中 %s 条知识", len(fallback_hits))

    docs: list[dict] = []
    blocks: list[str] = []
    for index, item in enumerate(hits, start=1):
        snippet = _build_doc_snippet(item.get("content", ""))
        docs.append(
            {
                "title": item.get("title") or item.get("source_title") or "未命名知识",
                "source": item.get("source") or "",
                "score": item.get("score", 0),
                "snippet": snippet,
            }
        )
        blocks.append(
            f"[知识{index}]\n"
            f"标题：{item.get('title') or item.get('source_title') or '未命名知识'}\n"
            f"来源：{item.get('source') or 'unknown'}\n"
            f"内容：{item.get('content') or ''}"
        )

    context = (
        "以下是与用户问题相关的知识库内容，请优先依据这些资料回答。"
        "如果知识库没有明确说明，请明确表示不确定，不要编造制度或规则。\n\n"
        + "\n\n".join(blocks)
    )
    retrieval_state["status"] = "success"
    retrieval_state["docs"] = docs
    if retrieval_state.get("mode") == "vector":
        retrieval_state["message"] = f"命中 {len(docs)} 条知识"
    logger.info("[知识库] 命中 %s 条知识", len(docs))
    return context, docs, retrieval_state


# ──────────────────── Anthropic (Claude) ────────────────────


async def _stream_anthropic(
    provider: str, api_key: str, api_url: str, model: str,
    system_prompt: str, messages: list[dict],
    temperature: float, max_tokens: int,
    usage: dict,
) -> AsyncGenerator[str, None]:
    import anthropic

    base_url = _normalize_api_base(provider, api_url)
    multimodal_msgs = _build_anthropic_messages(messages)

    client = anthropic.AsyncAnthropic(
        api_key=api_key,
        **({"base_url": base_url} if base_url else {}),
    )
    async with client.messages.stream(
        model=model,
        max_tokens=max_tokens,
        temperature=temperature,
        system=system_prompt,
        messages=multimodal_msgs,
    ) as stream:
        async for text in stream.text_stream:
            yield text
        resp = await stream.get_final_message()
        usage["input_tokens"] = resp.usage.input_tokens
        usage["output_tokens"] = resp.usage.output_tokens


# ──────────────────── OpenAI (GPT) / 智谱 (GLM) ────────────────────


async def _stream_openai(
    provider: str, api_key: str, api_url: str, model: str,
    system_prompt: str, messages: list[dict],
    temperature: float, max_tokens: int,
    usage: dict,
) -> AsyncGenerator[str, None]:
    from openai import AsyncOpenAI

    base_url = _normalize_api_base(provider, api_url)
    multimodal_msgs = _build_openai_messages(messages)

    client = AsyncOpenAI(
        api_key=api_key,
        **({"base_url": base_url} if base_url else {}),
    )
    full_messages = [{"role": "system", "content": system_prompt}] + multimodal_msgs
    stream = await client.chat.completions.create(
        model=model,
        messages=full_messages,
        temperature=temperature,
        max_tokens=max_tokens,
        stream=True,
        stream_options={"include_usage": True},
    )
    async for chunk in stream:
        if chunk.choices and chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content
        if chunk.usage:
            usage["input_tokens"] = chunk.usage.prompt_tokens or 0
            usage["output_tokens"] = chunk.usage.completion_tokens or 0


# ──────────────────── Google (Gemini) ────────────────────


async def _stream_google(
    provider: str, api_key: str, api_url: str, model: str,
    system_prompt: str, messages: list[dict],
    temperature: float, max_tokens: int,
    usage: dict,
) -> AsyncGenerator[str, None]:
    from google import genai
    from google.genai import types

    base_url = _normalize_api_base(provider, api_url)
    client = genai.Client(
        api_key=api_key,
        **({"http_options": types.HttpOptions(base_url=base_url)} if base_url else {}),
    )

    contents = _build_google_contents(messages)

    config = types.GenerateContentConfig(
        system_instruction=system_prompt,
        temperature=temperature,
        max_output_tokens=max_tokens,
    )
    async for chunk in client.aio.models.generate_content_stream(
        model=model, contents=contents, config=config,
    ):
        if chunk.text:
            yield chunk.text
        if chunk.usage_metadata:
            usage["input_tokens"] = chunk.usage_metadata.prompt_token_count or 0
            usage["output_tokens"] = chunk.usage_metadata.candidates_token_count or 0


# ──────────────────── 厂商路由表 ────────────────────


_PROVIDER_MAP = {
    "claude": _stream_anthropic,
    "openai": _stream_openai,
    "gemini": _stream_google,
    "zhipu": _stream_openai,
}


# ──────────────────── 主入口 ────────────────────


async def stream_ai_response(
    message: str,
    conversation_id: int,
    user_id: int,
    db: AsyncSession,
    usage: dict,
    retrieval: dict | None = None,
) -> AsyncGenerator[str, None]:
    """
    流式调用 AI 大模型。
    usage dict 在流结束后被填充: model / input_tokens / output_tokens。
    默认模型优先；如果调用失败，自动切换到下一个启用的模型。
    """
    # 1. 加载所有启用的模型（默认优先）
    providers = await _load_active_providers(db)
    if not providers:
        raise RuntimeError("未配置可用大模型，请在管理后台「大模型配置」中添加并启用")

    # 2. 加载 AI 行为配置
    ai_cfg = await _load_ai_config(db)
    system_prompt = ai_cfg.get("system_prompt", "你是一个专业的客服助手。")
    temperature = _parse_float(ai_cfg.get("temperature"), 0.7)
    max_tokens = _parse_int(ai_cfg.get("max_tokens"), 2048)

    # 3. 加载会话历史（已包含刚提交的用户消息）
    history = await _load_history(db, conversation_id)

    # 3.1 检索知识库（命中后再增强 system_prompt）
    knowledge_context, docs, retrieval_state = await _retrieve_knowledge_docs(message, ai_cfg, db)
    if retrieval is not None:
        retrieval.clear()
        retrieval.update(retrieval_state)
    if knowledge_context:
        system_prompt = f"{system_prompt}\n\n{knowledge_context}"

    # 4. 按顺序尝试每个模型，失败自动切换
    last_error: Exception | None = None
    for i, prov in enumerate(providers):
        provider_key = _normalize_provider(prov.provider)
        stream_fn = _PROVIDER_MAP.get(provider_key)
        if not stream_fn:
            logger.warning("[AI] 跳过不支持的厂商: %s (model=%s)", prov.provider, prov.model)
            continue

        try:
            logger.info("[AI] 开始生成 | user=%s conv=%s provider=%s model=%s%s",
                        user_id, conversation_id, provider_key, prov.model,
                        "" if i == 0 else f" (第{i+1}次切换)")

            usage["model"] = prov.model
            usage["input_price"] = float(prov.input_price) if prov.input_price else 0.0
            usage["output_price"] = float(prov.output_price) if prov.output_price else 0.0
            chunks: list[str] = []
            async for chunk in stream_fn(
                provider=provider_key,
                api_key=prov.api_key,
                api_url=prov.api_url,
                model=prov.model,
                system_prompt=system_prompt,
                messages=history,
                temperature=temperature,
                max_tokens=max_tokens,
                usage=usage,
            ):
                chunks.append(chunk)
                yield chunk

            logger.info("[AI] 完成 | user=%s conv=%s provider=%s model=%s in=%s out=%s",
                        user_id, conversation_id, provider_key, prov.model,
                        usage.get("input_tokens", 0), usage.get("output_tokens", 0))
            return  # 成功，结束

        except Exception as exc:
            last_error = exc
            if chunks:
                logger.error("[AI] 流式中途失败，已有部分输出，不再切换 | provider=%s model=%s err=%s",
                             provider_key, prov.model, exc)
                return  # 已经输出了部分内容，不能切换
            logger.warning("[AI] 调用失败，尝试下一个模型 | provider=%s model=%s err=%s",
                           provider_key, prov.model, exc)
            continue

    raise RuntimeError(f"所有模型均调用失败: {last_error}")
