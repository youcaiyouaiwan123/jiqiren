import logging

import redis.asyncio as aioredis

from app.config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()

redis_client: aioredis.Redis | None = None

# Lua: INCR + EXPIRE 原子执行，仅在 key 首次创建时设置 TTL，避免进程崩溃后 key 永不过期
_LUA_INCR_WITH_TTL = (
    "local n = redis.call('INCR', KEYS[1])\n"
    "if n == 1 then redis.call('EXPIRE', KEYS[1], ARGV[1]) end\n"
    "return n"
)


async def atomic_incr(client: aioredis.Redis, key: str, ttl: int) -> int:
    """原子地递增计数器并在首次创建时设置 TTL。"""
    return int(await client.eval(_LUA_INCR_WITH_TTL, 1, key, str(ttl)))


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
