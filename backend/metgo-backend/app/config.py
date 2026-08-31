from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    PROJECT_NAME: str = "METGO 3D"
    VERSION: str = "1.0.0"

    # Base de datos — definir DATABASE_URL en .env / Render (sin password en código)
    DATABASE_URL: str = "postgresql://user:CHANGE_ME@localhost:5432/metgodb"

    # JWT — obligatorio en producción
    SECRET_KEY: str = ""
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 2

    SMTP_SERVER: str = "smtp.mailgun.org"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""

    STRIPE_SECRET_KEY: Optional[str] = None
    STRIPE_WEBHOOK_SECRET: Optional[str] = None

    class Config:
        env_file = ".env"


def _require_secret_in_prod(settings: Settings) -> Settings:
    env = (os.getenv("METGO_ENV") or os.getenv("FLASK_ENV") or "").strip().lower()
    is_prod = env in ("production", "prod") or bool(os.getenv("RENDER"))
    secret = (settings.SECRET_KEY or os.getenv("METGO_JWT_SECRET") or "").strip()
    if is_prod and not secret:
        raise RuntimeError("SECRET_KEY o METGO_JWT_SECRET requerido en producción")
    if not settings.SECRET_KEY:
        settings.SECRET_KEY = secret or "ci-dev-only-not-for-production-use!!!!!!"
    return settings


settings = _require_secret_in_prod(Settings())
