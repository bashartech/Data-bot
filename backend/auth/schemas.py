from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    email: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserResponse"


class UserResponse(BaseModel):
    id: UUID
    email: str
    name: str
    picture: str | None
    created_at: datetime
    last_login: datetime


class LogoutResponse(BaseModel):
    message: str = "Logged out successfully"
