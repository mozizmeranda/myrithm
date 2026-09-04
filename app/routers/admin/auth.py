from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.schemas.auth import LoginRequest, TokenResponse
from app.services.auth_service import AuthService
from app.rate_limiter import auth_limiter
from app.errors import AppException
from app.config import settings

router = APIRouter(prefix="/api/v1/admin/auth", tags=["Admin Auth"])
auth_service = AuthService()

@router.post("/login", response_model=TokenResponse, dependencies=[Depends(auth_limiter)])
async def admin_login(req: LoginRequest, response: Response, db: Session = Depends(get_db)):
    token_resp, refresh_token, expire_seconds = await auth_service.login(db, req.email, req.password, required_role="admin")

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        max_age=expire_seconds,
        samesite="lax",
        secure=(settings.APP_ENV == "production")
    )
    return token_resp

