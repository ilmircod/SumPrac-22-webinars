import aioredis

from core.config import settings


async def get_redis() -> aioredis.Redis:
    return aioredis.from_url(settings.redis_dsn)
