import uuid
import jwt
from datetime import datetime, timedelta, timezone
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, InvalidHashError
from app.config import settings
from app.errors import AppException

ph = PasswordHasher()

def hash_password(password: str) -> str:
    return ph.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return ph.verify(hashed_password, plain_password)
    except (VerifyMismatchError, InvalidHashError):
        return False

def validate_password_strength(password: str):
    if not password or len(password) < 6:
        raise AppException(
            code="WEAK_PASSWORD",
            message="Password must be at least 6 characters long",
            status_code=422
        )

def create_access_token(user_id: str, role: str) -> str:
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": str(user_id),
        "role": role,
        "type": "access",
        "exp": expire,
        "iat": now
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm="HS256")

def create_refresh_token(user_id: str) -> tuple[str, str, int]:
    jti = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    expire_delta = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    expire = now + expire_delta
    payload = {
        "sub": str(user_id),
        "jti": jti,
        "type": "refresh",
        "exp": expire,
        "iat": now
    }
    token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm="HS256")
    expire_seconds = int(expire_delta.total_seconds())
    return token, jti, expire_seconds

def decode_token(token: str, expected_type: str | None = None) -> dict:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=["HS256"])
        if expected_type and payload.get("type") != expected_type:
            raise AppException("UNAUTHORIZED", f"Invalid token type. Expected {expected_type}", 401)
        return payload
    except jwt.ExpiredSignatureError:
        raise AppException("UNAUTHORIZED", "Token has expired", 401)
    except jwt.InvalidTokenError:
        raise AppException("UNAUTHORIZED", "Invalid token", 401)

