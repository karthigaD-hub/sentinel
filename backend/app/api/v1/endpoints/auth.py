from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_db
from app.schemas import LoginRequest, MessageResponse, TokenResponse, UserCreate, UserRead
from app.security.auth import AuthService
from app.security.dependencies import get_current_user
from app.models import User

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserRead, status_code=201)
async def register(data: UserCreate, session: AsyncSession = Depends(get_db)) -> User:
    try:
        return await AuthService.register(data, session)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc

@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, session: AsyncSession = Depends(get_db)) -> TokenResponse:
    try:
        return await AuthService.login(data, session)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc

@router.post("/refresh", response_model=TokenResponse)
async def refresh(refresh_token: str, session: AsyncSession = Depends(get_db)) -> TokenResponse:
    try:
        return await AuthService.refresh(refresh_token, session)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc

@router.post("/logout", response_model=MessageResponse)
async def logout(user: User = Depends(get_current_user), session: AsyncSession = Depends(get_db)) -> MessageResponse:
    from sqlalchemy import update
    from datetime import datetime, timezone
    await session.execute(update(__import__("app.models", fromlist=["RefreshToken"]).RefreshToken).where(__import__("app.models", fromlist=["RefreshToken"]).RefreshToken.user_id == user.id).values(revoked_at=datetime.now(timezone.utc)))
    await session.commit()
    return MessageResponse(message="Logged out")

@router.get("/me", response_model=UserRead)
async def me(user: User = Depends(get_current_user)) -> User:
    return user

@router.post("/verify-email", response_model=MessageResponse)
async def verify_email() -> MessageResponse:
    raise HTTPException(status_code=501, detail="Email delivery and verification tokens are not configured")

@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password() -> MessageResponse:
    raise HTTPException(status_code=501, detail="Password reset delivery is not configured")

@router.post("/reset-password", response_model=MessageResponse)
async def reset_password() -> MessageResponse:
    raise HTTPException(status_code=501, detail="Password reset tokens are not configured")
