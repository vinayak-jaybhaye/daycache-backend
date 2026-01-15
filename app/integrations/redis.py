import logging
from redis import Redis
from app.core.config import settings

logger = logging.getLogger(__name__)

redis_client: Redis | None = None

def get_redis_client() -> Redis:
    global redis_client
    if redis_client is None:
        try:
            redis_client = Redis.from_url(
                settings.REDIS_URL,
                decode_responses=True
            )
        except Redis.Error as exc:
            logger.exception("Failed to connect to Redis")
            raise
    return redis_client
