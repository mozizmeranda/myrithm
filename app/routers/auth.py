from fastapi import APIRouter, Depends, Request, Response, Cookie, status
from sqlalchemy.orm import Session
from app.dependencies import get_db, get_current_user
from app.schemas.auth import RegisterRequest, LoginRequest, ChangePasswordRequest, UserResponse, TokenResponse
from app.services.auth_service import AuthService
from app.rate_limiter import auth_limiter
from app.models.user import User
from app.config import settings

router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])
auth_service = AuthService()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(auth_limiter)])
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    return auth_service.register(db, req.email, req.password)

@router.post("/login", response_model=TokenResponse, dependencies=[Depends(auth_limiter)])
async def login(req: LoginRequest, response: Response, db: Session = Depends(get_db)):
    token_resp, refresh_token, expire_seconds = await auth_service.login(db, req.email, req.password)
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        max_age=expire_seconds,
        samesite="lax",
        secure=(settings.APP_ENV == "production")
    )
    return token_resp

@router.post("/refresh", response_model=TokenResponse, dependencies=[Depends(auth_limiter)])
async def refresh(
    response: Response,
    refresh_token: str | None = Cookie(default=None),
    db: Session = Depends(get_db)
):
    token_resp, new_refresh_token, expire_seconds = await auth_service.refresh(db, refresh_token or "")
    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        max_age=expire_seconds,
        samesite="lax",
        secure=(settings.APP_ENV == "production")
    )
    return token_resp

@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(response: Response, refresh_token: str | None = Cookie(default=None)):
    await auth_service.logout(refresh_token or "")
    response.delete_cookie("refresh_token")
    return {"message": "Successfully logged out"}

@router.post("/change-password", status_code=status.HTTP_200_OK, dependencies=[Depends(auth_limiter)])
async def change_password(
    req: ChangePasswordRequest,
    response: Response,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    await auth_service.change_password(db, current_user.id, req.current_password, req.new_password)
    response.delete_cookie("refresh_token")
    return {"message": "Password changed successfully. Please log in again."}
