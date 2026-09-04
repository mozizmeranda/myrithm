import time
from fastapi import Request
from app.redis_client import redis_client, check_redis_health
from app.errors import AppException

# In-memory rate limiting storage (fallback when Redis is not running)
_in_memory_rate_limits: dict[str, list[float]] = {}  # key -> list of timestamps

class RateLimiter:
    def __init__(self, times: int = 10, seconds: int = 60):
        self.times = times
        self.seconds = seconds

    async def __call__(self, request: Request):
        client_ip = request.client.host if request.client else "127.0.0.1"
        route_path = request.url.path
        key = f"rate_limit:{route_path}:{client_ip}"

        # 1. Try Redis if available
        try:
            if await check_redis_health():
                current = await redis_client.get(key)
                if current is not None and int(current) >= self.times:
                    raise AppException("RATE_LIMIT_EXCEEDED", "Too many requests. Please try again later.", 429)
                
                async with redis_client.pipeline(transaction=True) as pipe:
                    pipe.incr(key)
                    if current is None:
                        pipe.expire(key, self.seconds)
                    await pipe.execute()
                return
        except AppException:
            raise
        except Exception:
            pass

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
