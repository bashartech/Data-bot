from urllib.parse import urlencode

import httpx
from google.auth.transport.requests import Request as GoogleRequest
from google.oauth2 import id_token
from sqlalchemy.ext.asyncio import AsyncSession

from auth.service import AuthService, AuthError, create_access_token
from config.logging import logger
from config.settings import settings
from repositories.allowed_user_repo import AllowedUserRepository
from repositories.user_repo import UserRepository


def build_google_auth_url(redirect_uri: str) -> str:
    params = {
        "client_id": settings.google_client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "consent",
    }
    return f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"


async def exchange_code_for_token(code: str, redirect_uri: str) -> dict:
    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "code": code,
        "client_id": settings.google_client_id,
        "client_secret": settings.google_client_secret,
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code",
    }
    async with httpx.AsyncClient() as client:
        resp = await client.post(token_url, data=data)
        resp.raise_for_status()
        return resp.json()


async def verify_google_id_token(id_token_str: str) -> dict:
    try:
        info = id_token.verify_oauth2_token(
            id_token_str,
            GoogleRequest(),
            settings.google_client_id,
        )
    except Exception as e:
        logger.error("Google token verification failed", error=str(e))
        raise AuthError("Invalid Google ID token")

    if info.get("iss") not in [
        "accounts.google.com",
        "https://accounts.google.com",
    ]:
        raise AuthError("Invalid token issuer")

    if not info.get("email_verified", False):
        raise AuthError("Email not verified by Google")

    return info


async def google_login(
    code: str, redirect_uri: str, session: AsyncSession
) -> tuple[str, dict]:
    token_data = await exchange_code_for_token(code, redirect_uri)
    id_token_str = token_data.get("id_token")
    if not id_token_str:
        raise AuthError("No ID token in Google response")

    info = await verify_google_id_token(id_token_str)
    email = info.get("email", "").strip().lower()
    name = info.get("name", email.split("@")[0])
    picture = info.get("picture")

    if settings.auth_mode == "allowlist":
        allowed_user_repo = AllowedUserRepository(session)
        allowed = await allowed_user_repo.is_allowed(email)
        if not allowed:
            logger.warning("Google login denied - email not in allowlist", email=email)
            raise AuthError("Email is not authorized", status_code=403)
    elif settings.auth_mode == "workspace":
        domain = email.split("@")[1] if "@" in email else ""
        if domain != settings.allowed_domain:
            logger.warning("Google login denied - invalid domain", email=email, domain=domain)
            raise AuthError("Domain is not authorized", status_code=403)

    user_repo = UserRepository(session)
    user = await user_repo.upsert(email=email, name=name, picture=picture)
    await session.commit()

    token = create_access_token(user.id)
    logger.info("Google login successful", user_id=str(user.id), email=email)

    return token, {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "picture": user.picture,
        "created_at": user.created_at,
        "last_login": user.last_login,
    }
