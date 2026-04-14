import logging

import redis.asyncio as aioredis

from app.config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()

redis_client: aioredis.Redis | None = None


async def init_redis() -> aioredis.Redis | None:
    global redis_client
    logger.info("[Redis] 连接中... url=%s", settings.redis_url.split("@")[-1] if "@" in settings.redis_url else settings.redis_url)
    client = aioredis.from_url(
        settings.redis_url,
        decode_responses=True,
    )
    try:
        await client.ping()
    except Exception as exc:
        redis_client = None
        try:
            await client.close()
        except Exception:
            pass
        logger.warning("[Redis] unavailable, running in degraded mode | %s", exc)
        return None
    redis_client = client
    logger.info("[Redis] 连接成功")
    return redis_client


async def close_redis() -> None:
    global redis_client
    if redis_client:
        await redis_client.close()
        redis_client = None
        logger.info("[Redis] 连接已关闭")


def get_redis(*, required: bool = True) -> aioredis.Redis | None:
    if redis_client is None:
        if required:
            raise RuntimeError("Redis not initialized. Call init_redis() first.")
        return None
    return redis_client
