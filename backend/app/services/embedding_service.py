import logging
from typing import Any, Sequence
from urllib.parse import urlsplit, urlunsplit

from openai import AsyncOpenAI
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.llm_provider import LlmProvider

logger = logging.getLogger(__name__)

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

_DEFAULT_EMBEDDING_MODELS = {
    "openai": "text-embedding-3-small",
    "zhipu": "embedding-3",
    "gemini": "text-embedding-004",
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


async def _load_embedding_provider(db: AsyncSession, provider_name: str | None) -> LlmProvider:
    provider_key = _normalize_provider(provider_name or "")
    if provider_key not in {"openai", "zhipu", "gemini"}:
        raise RuntimeError(f"不支持的 embedding 厂商: {provider_name or ''}")

    stmt = (
        select(LlmProvider)
        .where(LlmProvider.is_active == 1)
        .order_by(LlmProvider.is_default.desc(), LlmProvider.id.desc())
    )
    rows = (await db.execute(stmt)).scalars().all()
    for row in rows:
        if _normalize_provider(row.provider) == provider_key:
            return row
    raise RuntimeError(f"未找到可用的 embedding 厂商配置: {provider_key}")


async def _embed_openai(provider: LlmProvider, model: str, texts: Sequence[str]) -> list[list[float]]:
    base_url = _normalize_api_base(_normalize_provider(provider.provider), provider.api_url)
    client = AsyncOpenAI(
        api_key=provider.api_key,
        **({"base_url": base_url} if base_url else {}),
    )
    response = await client.embeddings.create(model=model, input=list(texts))
    return [item.embedding for item in response.data]


async def _embed_google(provider: LlmProvider, model: str, texts: Sequence[str]) -> list[list[float]]:
    from google import genai
    from google.genai import types

    base_url = _normalize_api_base(_normalize_provider(provider.provider), provider.api_url)
    client = genai.Client(
        api_key=provider.api_key,
        **({"http_options": types.HttpOptions(base_url=base_url)} if base_url else {}),
    )
    vectors: list[list[float]] = []
    for text in texts:
        response = await client.aio.models.embed_content(
            model=model,
            contents=text,
        )
        embedding = getattr(response, "embeddings", None) or []
        if not embedding:
            raise RuntimeError("Gemini embedding 返回为空")
        values = getattr(embedding[0], "values", None)
        if not values:
            raise RuntimeError("Gemini embedding 返回格式异常")
        vectors.append(list(values))
    return vectors


async def embed_texts(
    db: AsyncSession,
    texts: Sequence[str],
    provider_name: str | None,
    model_name: str | None = None,
    runtime_meta: dict[str, Any] | None = None,
) -> list[list[float]]:
    clean_texts = [text.strip() for text in texts if text and text.strip()]
    if not clean_texts:
        return []
    provider = await _load_embedding_provider(db, provider_name)
    provider_key = _normalize_provider(provider.provider)
    model = (model_name or "").strip() or _DEFAULT_EMBEDDING_MODELS[provider_key]
    base_url = _normalize_api_base(provider_key, provider.api_url)
    if runtime_meta is not None:
        runtime_meta["provider"] = provider_key
        runtime_meta["model"] = model
        runtime_meta["base_url"] = base_url or ""
        runtime_meta["provider_row_id"] = provider.id
    logger.info("[知识库] 开始 embedding | provider=%s model=%s count=%s", provider_key, model, len(clean_texts))
    try:
        if provider_key in {"openai", "zhipu"}:
            return await _embed_openai(provider, model, clean_texts)
        if provider_key == "gemini":
            return await _embed_google(provider, model, clean_texts)
        raise RuntimeError(f"暂不支持的 embedding 厂商: {provider_key}")
    except Exception as exc:
        raise RuntimeError(
            f"Embedding 调用失败(provider={provider_key}, model={model}, base_url={base_url or 'default'}): {exc}"
        ) from exc
