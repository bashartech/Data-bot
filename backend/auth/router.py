from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import get_current_user
from auth.google import build_google_auth_url, google_login
from auth.schemas import LoginRequest, LoginResponse, LogoutResponse, UserResponse
from auth.service import AuthError, AuthService
from config.settings import settings
from database.engine import get_session

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/login",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
)
async def login_email(body: LoginRequest, session: AsyncSession = Depends(get_session)):
    service = AuthService(session)
    try:
        token, user_data = await service.login(body.email)
    except AuthError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)

    return LoginResponse(
        access_token=token,
        user=UserResponse(**user_data),
    )


@router.get("/login")
async def login_google():
    auth_url = build_google_auth_url(settings.auth_redirect_uri)
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url=auth_url)


@router.get("/callback")
async def auth_callback(
    request: Request,
    code: str | None = None,
    error: str | None = None,
    session: AsyncSession = Depends(get_session),
):
    if error:
        raise HTTPException(status_code=400, detail=f"Google auth error: {error}")

    if not code:
        raise HTTPException(status_code=400, detail="Missing authorization code")

    try:
        token, user_data = await google_login(code, settings.auth_redirect_uri, session)
    except AuthError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)

    frontend_url = settings.cors_origins[0]
    redirect_target = f"{frontend_url}/auth/callback?token={token}"
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url=redirect_target)


@router.get("/me", response_model=UserResponse)
async def me(current_user: dict = Depends(get_current_user)):
    return UserResponse(**current_user)


@router.post("/logout", response_model=LogoutResponse)
async def logout(current_user: dict = Depends(get_current_user)):
    return LogoutResponse()
