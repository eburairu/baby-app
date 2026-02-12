"""環境変数管理"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """アプリケーション設定"""
    DATABASE_URL: str
    SECRET_KEY: str
    SYSTEM_INVITE_CODE: str
    ENVIRONMENT: str = "development"
    TIMEZONE: str = "Asia/Tokyo"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

# PostgreSQL URLの調整（Renderの互換性）
if settings.DATABASE_URL.startswith("postgres://"):
    settings.DATABASE_URL = settings.DATABASE_URL.replace(
        "postgres://", "postgresql://", 1
    )
