import time
import logging
import redis.asyncio as aioredis
from app.config import settings

logger = logging.getLogger(__name__)

# Real Redis client
redis_client = aioredis.from_url(
    settings.REDIS_URL,
    decode_responses=True,
    socket_timeout=1.0
)

# In-Memory fallback storage (used when Redis is not running/installed)
_in_memory_refresh_tokens: dict[str, tuple[str, float]] = {}  # jti -> (user_id, expire_at)
_in_memory_user_tokens: dict[str, set[str]] = {}  # user_id -> set(jti)
_in_memory_leads: dict[str, int] = {}  # stream_code -> count

async def check_redis_health() -> bool:
    try:
        await redis_client.ping()
        return True
    except Exception:
        return False

def _cleanup_expired_memory_tokens():
    now = time.time()
    expired_jtis = [jti for jti, (_, exp) in _in_memory_refresh_tokens.items() if exp <= now]
    for jti in expired_jtis:
        user_id, _ = _in_memory_refresh_tokens.pop(jti)
        if user_id in _in_memory_user_tokens:
            _in_memory_user_tokens[user_id].discard(jti)

async def add_refresh_token(user_id: str, jti: str, expire_seconds: int):
    expire_at = time.time() + expire_seconds
    try:
        if await check_redis_health():
            key = f"refresh:{jti}"
            user_tokens_key = f"user_tokens:{user_id}"
            async with redis_client.pipeline(transaction=True) as pipe:
                pipe.set(key, user_id, ex=expire_seconds)
                pipe.sadd(user_tokens_key, jti)
                pipe.expire(user_tokens_key, expire_seconds)
                await pipe.execute()
            return
    except Exception:
        pass

    # Fallback to In-Memory
    _cleanup_expired_memory_tokens()
    _in_memory_refresh_tokens[jti] = (str(user_id), expire_at)
    if str(user_id) not in _in_memory_user_tokens:
        _in_memory_user_tokens[str(user_id)] = set()
    _in_memory_user_tokens[str(user_id)].add(jti)

async def is_refresh_token_valid(user_id: str, jti: str) -> bool:
    try:
        if await check_redis_health():
            key = f"refresh:{jti}"
            val = await redis_client.get(key)
            return val == str(user_id)
    except Exception:
        pass

    # Fallback to In-Memory
    _cleanup_expired_memory_tokens()
    if jti in _in_memory_refresh_tokens:
        stored_uid, expire_at = _in_memory_refresh_tokens[jti]
        if stored_uid == str(user_id) and expire_at > time.time():
            return True
    return False

async def revoke_refresh_token(jti: str):
    try:
        if await check_redis_health():
            key = f"refresh:{jti}"
            user_id = await redis_client.get(key)
            if user_id:
                user_tokens_key = f"user_tokens:{user_id}"
                await redis_client.srem(user_tokens_key, jti)
                await redis_client.delete(key)
            return
    except Exception:
        pass

    # Fallback to In-Memory
    if jti in _in_memory_refresh_tokens:
        user_id, _ = _in_memory_refresh_tokens.pop(jti)
        if user_id in _in_memory_user_tokens:
            _in_memory_user_tokens[user_id].discard(jti)

async def revoke_all_user_refresh_tokens(user_id: str):
    uid_str = str(user_id)
    try:
        if await check_redis_health():
            user_tokens_key = f"user_tokens:{uid_str}"
            jtis = await redis_client.smembers(user_tokens_key)
            if jtis:
                keys = [f"refresh:{jti}" for jti in jtis]
                keys.append(user_tokens_key)
                await redis_client.delete(*keys)
            else:
                await redis_client.delete(user_tokens_key)
            return
    except Exception:
        pass

    # Fallback to In-Memory
    jtis = _in_memory_user_tokens.pop(uid_str, set())
    for jti in jtis:
        _in_memory_refresh_tokens.pop(jti, None)

async def increment_lead_counter(stream_code: str):
    try:
        if await check_redis_health():
            key = f"lead_counter:{stream_code}"
            await redis_client.incr(key)
            return
    except Exception:
        pass

    _in_memory_leads[stream_code] = _in_memory_leads.get(stream_code, 0) + 1
