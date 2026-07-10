from datetime import datetime, timedelta, timezone
from uuid import UUID

from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from config.logging import logger
from config.settings import settings
from repositories.allowed_user_repo import AllowedUserRepository
from repositories.user_repo import UserRepository


class AuthError(Exception):
    def __init__(self, message: str, status_code: int = 401):
        self.message = message
        self.status_code = status_code


def create_access_token(user_id: UUID) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.session_expiry_minutes
    )
    payload = {
        "sub": str(user_id),
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, settings.session_secret_key, algorithm="HS256")


def verify_access_token(token: str) -> UUID:
    try:
        payload = jwt.decode(
            token, settings.session_secret_key, algorithms=["HS256"]
        )
        user_id = payload.get("sub")
        if user_id is None:
            raise AuthError("Invalid token payload")
        return UUID(user_id)
    except JWTError:
        raise AuthError("Invalid or expired token")


class AuthService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repo = UserRepository(session)
        self.allowed_user_repo = AllowedUserRepository(session)

    async def login(self, email: str) -> tuple[str, dict]:
        email = email.strip().lower()

        if settings.auth_mode == "allowlist":
            allowed = await self.allowed_user_repo.is_allowed(email)
            if not allowed:
                logger.warning("Login denied - email not in allowlist", email=email)
                raise AuthError("Email is not authorized", status_code=403)
        elif settings.auth_mode == "workspace":
            if not email.endswith(f"@{settings.allowed_domain}"):
                logger.warning("Login denied - domain not allowed", email=email)
                raise AuthError("Domain is not authorized", status_code=403)

        name = email.split("@")[0]
        if settings.auth_mode == "allowlist":
            from models.allowed_user import AllowedUser
            from sqlalchemy import select
            result = await self.session.execute(
                select(AllowedUser).where(AllowedUser.email == email)
            )
            allowed_user = result.scalar_one_or_none()
            if allowed_user and allowed_user.full_name:
                name = allowed_user.full_name

        user = await self.user_repo.upsert(email=email, name=name)
        await self.session.commit()

        token = create_access_token(user.id)
        logger.info("User logged in", user_id=str(user.id), email=email)

        return token, {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "picture": user.picture,
            "created_at": user.created_at,
            "last_login": user.last_login,
        }

    async def get_user(self, user_id: UUID) -> dict | None:
        user = await self.user_repo.get_by_id(user_id)
        if user is None:
            return None
        return {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "picture": user.picture,
            "created_at": user.created_at,
            "last_login": user.last_login,
        }
