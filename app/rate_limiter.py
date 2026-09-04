import time
import logging
from fastapi import Request
from app.redis_client import redis_client, check_redis_health
from app.errors import AppException

logger = logging.getLogger(__name__)

# In-memory rate limiting storage (fallback when Redis is not running)
_in_memory_rate_limits: dict[str, list[float]] = {}  # key -> list of timestamps

def get_client_ip(request: Request) -> str:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "127.0.0.1"

def reset_rate_limiter_state():
    _in_memory_rate_limits.clear()

class RateLimiter:
    def __init__(self, times: int = 10, seconds: int = 60):
        self.times = times
        self.seconds = seconds

    async def __call__(self, request: Request):
        client_ip = get_client_ip(request)
        route_path = request.url.path
        key = f"rate_limit:{route_path}:{client_ip}"

        # 1. Try Redis if available
        try:
            if await check_redis_health():
                current = await redis_client.incr(key)
                if current == 1:
                    await redis_client.expire(key, self.seconds)
                if current > self.times:
                    raise AppException("RATE_LIMIT_EXCEEDED", "Too many requests. Please try again later.", 429)
                return
        except AppException:
            raise
        except Exception as e:
            logger.warning("Redis rate limiter error, falling back to memory: %s", e)

        # 2. In-Memory Rate Limiting Fallback (if Redis is not running)
        now = time.time()
        timestamps = _in_memory_rate_limits.get(key, [])
        # Keep only timestamps within window
        timestamps = [t for t in timestamps if now - t < self.seconds]

        if len(timestamps) >= self.times:
            raise AppException("RATE_LIMIT_EXCEEDED", "Too many requests. Please try again later.", 429)

        timestamps.append(now)
        _in_memory_rate_limits[key] = timestamps

auth_limiter = RateLimiter(times=5, seconds=60)
lead_limiter = RateLimiter(times=10, seconds=60)
sync_limiter = RateLimiter(times=30, seconds=60)

