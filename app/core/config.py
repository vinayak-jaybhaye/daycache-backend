from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    CLOUDINARY_CLOUD_NAME: str
    CLOUDINARY_API_KEY: str
    CLOUDINARY_API_SECRET: str
    CLOUDINARY_BASE_URL: str
    HUGGINGFACE_API_KEY: str
    GEMINI_API_KEY: str
    REDIS_URL: str
    RESEND_API_KEY: str
    SMTP_SERVER: str
    SMTP_PORT: str
    SMTP_USERNAME: str
    SMTP_PASSWORD: str

    class Config:
        env_file = ".env"


settings = Settings()
