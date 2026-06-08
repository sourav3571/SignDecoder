
import redis.asyncio as aioredis
from app.core.config import settings
import logging
from typing import Any, Optional
import json

logger = logging.getLogger(__name__)

redis_client: Optional[aioredis.Redis] = None

async def init_redis():

    global redis_client
    try:
        redis_client = await aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf8",
            decode_responses=True,
        )

        await redis_client.ping()
        logger.info("✓ Redis connection established")
    except Exception as e:
        logger.warning(f"⚠ Redis connection not available: {e}")
        raise

async def close_redis():

    global redis_client
    if redis_client:
        try:
            await redis_client.close()
            logger.info("✓ Redis connection closed")
        except Exception as e:
            logger.error(f"✗ Error closing Redis: {e}")
            raise

async def get_redis() -> aioredis.Redis:

    if redis_client is None:
        await init_redis()
    return redis_client

async def cache_get(key: str) -> Optional[Any]:

    try:
        client = await get_redis()
        value = await client.get(key)
        if value:
            return json.loads(value)
        return None
    except Exception as e:
        logger.warning(f"Cache get failed for key '{key}': {e}")
        return None

async def cache_set(
    key: str,
    value: Any,
    ttl: Optional[int] = None,
) -> bool:

    try:
        client = await get_redis()
        ttl = ttl or settings.REDIS_CACHE_TTL
        await client.setex(key, ttl, json.dumps(value))
        return True
    except Exception as e:
        logger.warning(f"Cache set failed for key '{key}': {e}")
        return False

async def cache_delete(key: str) -> bool:

    try:
        client = await get_redis()
        result = await client.delete(key)
        return result > 0
    except Exception as e:
        logger.warning(f"Cache delete failed for key '{key}': {e}")
        return False

async def cache_clear_pattern(pattern: str) -> int:

    try:
        client = await get_redis()
        keys = await client.keys(pattern)
        if keys:
            return await client.delete(*keys)
        return 0
    except Exception as e:
        logger.warning(f"Cache clear pattern failed for '{pattern}': {e}")
        return 0
