from sqlalchemy.orm import Session
from app.repositories.user_repository import UserRepository
from app.security import (
    hash_password,
    verify_password,
    validate_password_strength,
    create_access_token,
    create_refresh_token,
    decode_token
)
from app.redis_client import (
    add_refresh_token,
    is_refresh_token_valid,
    revoke_refresh_token,
    revoke_all_user_refresh_tokens
)
from app.errors import AppException
from app.schemas.auth import UserResponse, TokenResponse

class AuthService:
    def __init__(self):
        self.user_repo = UserRepository()

    def register(self, db: Session, email: str, password: str) -> UserResponse:
        validate_password_strength(password)
        hashed = hash_password(password)
        user = self.user_repo.create(db, email, hashed, role="user")
        return UserResponse.model_validate(user)

    async def login(self, db: Session, email: str, password: str) -> tuple[TokenResponse, str, int]:
        user = self.user_repo.get_by_email(db, email)
        if not user or not verify_password(password, user.password_hash):
            raise AppException("UNAUTHORIZED", "Invalid email or password", 401)

        access_token = create_access_token(user.id, user.role)
        refresh_token, jti, expire_seconds = create_refresh_token(user.id)
        await add_refresh_token(user.id, jti, expire_seconds)

        token_resp = TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user=UserResponse.model_validate(user)
        )
        return token_resp, refresh_token, expire_seconds

    async def refresh(self, db: Session, refresh_token_str: str) -> tuple[TokenResponse, str, int]:
        if not refresh_token_str:
            raise AppException("UNAUTHORIZED", "Refresh token is missing", 401)

        payload = decode_token(refresh_token_str)
        user_id = payload.get("sub")
        jti = payload.get("jti")

        if not user_id or not jti:
            raise AppException("UNAUTHORIZED", "Invalid refresh token format", 401)

        valid = await is_refresh_token_valid(user_id, jti)
        if not valid:
            raise AppException("UNAUTHORIZED", "Refresh token is invalid or revoked", 401)

        user = self.user_repo.get_by_id(db, user_id)
        if not user:
            raise AppException("UNAUTHORIZED", "User not found", 401)

        # Token Rotation: revoke old, create new
        await revoke_refresh_token(jti)

        new_access_token = create_access_token(user.id, user.role)
        new_refresh_token, new_jti, expire_seconds = create_refresh_token(user.id)
        await add_refresh_token(user.id, new_jti, expire_seconds)

        token_resp = TokenResponse(
            access_token=new_access_token,
            token_type="bearer",
            user=UserResponse.model_validate(user)
        )
        return token_resp, new_refresh_token, expire_seconds

    async def logout(self, refresh_token_str: str):
        if not refresh_token_str:
            return
        try:
            payload = decode_token(refresh_token_str)
            jti = payload.get("jti")
            if jti:
                await revoke_refresh_token(jti)
        except Exception:
            pass

    async def change_password(self, db: Session, user_id: str, current_password: str, new_password: str):
        user = self.user_repo.get_by_id(db, user_id)
        if not user:
            raise AppException("UNAUTHORIZED", "User not found", 401)

        if not verify_password(current_password, user.password_hash):
            raise AppException("INVALID_CURRENT_PASSWORD", "Current password is incorrect", 401)

        validate_password_strength(new_password)

        new_hashed = hash_password(new_password)
        self.user_repo.update_password(db, user_id, new_hashed)

        # Invalidate all active user refresh tokens across all devices
        await revoke_all_user_refresh_tokens(user_id)
