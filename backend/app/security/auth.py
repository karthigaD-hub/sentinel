from datetime import datetime, timezone
from uuid import uuid4
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security_config import create_access_token, create_refresh_token, hash_password, hash_refresh_token, verify_password
from app.models import RefreshToken, Role, User
from app.schemas import LoginRequest, TokenResponse, UserCreate

ROLE_PERMISSIONS: dict[str, list[str]] = {
    "admin": [
        "dashboard:view", "capture:view", "capture:start", "capture:stop",
        "detection:view", "alerts:view", "alerts:update", "threatintel:view",
        "assistant:use", "reports:view", "quantum:view", "settings:view", "settings:update", "admin:manage",
    ],
    "analyst": [
        "dashboard:view", "capture:view", "capture:start", "capture:stop",
        "detection:view", "alerts:view", "alerts:update", "threatintel:view",
        "assistant:use", "reports:view", "quantum:view", "settings:view",
    ],
    "viewer": [
        "dashboard:view", "alerts:view", "detection:view", "threatintel:view",
        "reports:view", "quantum:view", "settings:view",
    ],
}

class AuthService:
    @staticmethod
    async def _get_or_create_role(role_name: str, session: AsyncSession) -> Role:
        role = await session.scalar(select(Role).where(Role.name == role_name))
        if role:
            return role
        role = Role(name=role_name, permissions=ROLE_PERMISSIONS.get(role_name, []))
        session.add(role)
        await session.flush()
        return role

    @staticmethod
    async def register(data: UserCreate, session: AsyncSession) -> User:
        requested_role = data.role.lower().strip()
        if requested_role not in ROLE_PERMISSIONS:
            requested_role = "viewer"

        existing = await session.scalar(select(User).where(User.email == data.email.lower()))
        if existing:
            raise ValueError("An account with this email already exists")
        role = await AuthService._get_or_create_role(requested_role, session)
        user = User(email=data.email.lower(), password_hash=hash_password(data.password), full_name=data.full_name, role_id=role.id)
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user

    @staticmethod
    async def login(data: LoginRequest, session: AsyncSession) -> TokenResponse:
        user = await session.scalar(select(User).where(User.email == data.email.lower()))
        if not user or not verify_password(data.password, user.password_hash):
            raise ValueError("Invalid email or password")
        raw, hashed, expires = create_refresh_token()
        session.add(RefreshToken(token_hash=hashed, family_id=uuid4(), user_id=user.id, expires_at=expires))
        await session.commit()
        return TokenResponse(access_token=create_access_token(str(user.id)), refresh_token=raw)

    @staticmethod
    async def refresh(raw: str, session: AsyncSession) -> TokenResponse:
        token = await session.scalar(select(RefreshToken).where(RefreshToken.token_hash == hash_refresh_token(raw)))
        if not token or token.revoked_at or token.expires_at <= datetime.now(timezone.utc):
            if token:
                await session.execute(RefreshToken.__table__.update().where(RefreshToken.family_id == token.family_id).values(revoked_at=datetime.now(timezone.utc)))
                await session.commit()
            raise ValueError("Invalid refresh token")
        token.revoked_at = datetime.now(timezone.utc)
        new_raw, new_hash, expires = create_refresh_token()
        session.add(RefreshToken(token_hash=new_hash, family_id=token.family_id, user_id=token.user_id, expires_at=expires))
        await session.commit()
        return TokenResponse(access_token=create_access_token(str(token.user_id)), refresh_token=new_raw)
