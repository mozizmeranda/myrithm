from typing import Generator
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.security import decode_token
from app.repositories.user_repository import UserRepository
from app.models.user import User
from app.errors import AppException

security = HTTPBearer()
user_repo = UserRepository()

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    token = credentials.credentials
    payload = decode_token(token, expected_type="access")
    user_id = payload.get("sub")
    if not user_id:
        raise AppException("UNAUTHORIZED", "Invalid token payload", 401)

    user = user_repo.get_by_id(db, user_id)
    if not user:
        raise AppException("UNAUTHORIZED", "User not found or deleted", 401)

    return user

def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "admin":
        raise AppException("FORBIDDEN", "Administrator privileges required", 403)
    return current_user
