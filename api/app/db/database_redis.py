from redis.asyncio import Redis

from app.core.config import settings

HOST = settings.redis_host
PORT = settings.redis_port

redis = Redis(
    host=HOST,
    port=PORT,
    decode_responses=True
)