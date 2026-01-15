from pydantic_settings import BaseSettings
from typing import Optional, List


class Settings(BaseSettings):
    # App / Environment
    ENV: str = "development"

    CORS_ORIGINS: List[str] = None

    # Database
    DATABASE_URL: str

    # Auth / Security
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Redis (OTP, cache)
    REDIS_URL: Optional[str] = None

    # AI
    GEMINI_API_KEY: Optional[str] = None

    # Email (optional)
    SMTP_SERVER: Optional[str] = None
    SMTP_PORT: Optional[int] = None
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None

    # OAuth (optional)
    GOOGLE_CLIENT_ID: Optional[str] = None

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
