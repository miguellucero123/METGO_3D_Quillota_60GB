from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "METGO 3D"
    VERSION: str = "1.0.0"
    
    # Base de datos
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/metgodb"
    
    # JWT
    SECRET_KEY: str = "your-super-secret-key-for-jwt-metgo"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 2
    
    # SMTP Emails
    SMTP_SERVER: str = "smtp.mailgun.org"
    SMTP_PORT: int = 587
    SMTP_USER: str = "postmaster@tu-dominio.com"
    SMTP_PASSWORD: str = "your-password"
    
    # Stripe (Opcional por ahora)
    STRIPE_SECRET_KEY: Optional[str] = None
    STRIPE_WEBHOOK_SECRET: Optional[str] = None
    
    class Config:
        env_file = ".env"

settings = Settings()
