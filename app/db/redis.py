from datetime import timedelta

import redis.asyncio as redis

from app.core.config import settings

redis_client = None


async def get_redis():
    global redis_client
    if redis_client is None:
        if settings.redis_url.startswith("rediss://"):
            import ssl

            redis_client = await redis.from_url(
                settings.redis_url,
                encoding="utf-8",
                decode_responses=True,
                ssl=ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT),
                ssl_cert_reqs=ssl.CERT_NONE,
            )
        else:
            redis_client = await redis.from_url(
                settings.redis_url,
                encoding="utf-8",
                decode_responses=True,
            )
    return redis_client


async def close_redis():
    global redis_client
    if redis_client:
        await redis_client.close()
        redis_client = None


async def add_to_blacklist(token: str, expires_in: int):
    client = await get_redis()
    await client.setex(f"blacklist:{token}", timedelta(seconds=expires_in), "1")


async def is_blacklisted(token: str) -> bool:
    client = await get_redis()
    result = await client.exists(f"blacklist:{token}")
    return result > 0
