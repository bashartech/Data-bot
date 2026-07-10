from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


def _find_env_file() -> str | None:
    candidates = [
        Path(__file__).parent.parent.parent / ".env",
        Path.cwd() / ".env",
    ]
    for p in candidates:
        if p.exists():
            return str(p)
    return None


class Settings(BaseSettings):
    app_name: str = "Enterprise AI Chatbot"
    debug: bool = False

    groq_api_key: str
    groq_model: str = "openai/gpt-oss-120b"
    groq_temperature: float = 0.7
    groq_max_tokens: int = 2048

    neon_database_url: str

    google_client_id: str
    google_client_secret: str

    auth_mode: Literal["workspace", "allowlist"] = "allowlist"
    allowed_domain: str = ""

    session_secret_key: str = "change-me-in-production"
    session_expiry_minutes: int = 60

    auth_redirect_uri: str = "http://localhost:8000/auth/callback"

    cors_origin_string: str = "http://localhost:3001"

    @property
    def cors_origins(self) -> list[str]:
        return [o.strip() for o in self.cors_origin_string.split(",")]

    @property
    def async_database_url(self) -> str:
        return self.neon_database_url.replace(
            "postgresql://", "postgresql+asyncpg://", 1
        ).split("?")[0]

    model_config = SettingsConfigDict(
        env_file=_find_env_file(),
        env_file_encoding="utf-8",
    )


settings = Settings()
