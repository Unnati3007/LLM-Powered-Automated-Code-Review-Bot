import json
import os

import redis.asyncio as aioredis

_redis = None
TTL = 60 * 60 * 24 * 7  # 7 days


async def _get_redis():
    global _redis
    if _redis is None:
        _redis = await aioredis.from_url(
            os.environ.get("REDIS_URL", "redis://localhost:6379")
        )
    return _redis


async def get_cached_review(key: str) -> list[dict] | None:
    r = await _get_redis()
    val = await r.get(f"review:{key}")
    return json.loads(val) if val else None


async def set_cached_review(key: str, comments: list[dict]) -> None:
    r = await _get_redis()
    await r.setex(f"review:{key}", TTL, json.dumps(comments))
