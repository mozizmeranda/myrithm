from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_ENV: str = "development"
    APP_TIMEZONE: str = "Asia/Tashkent"

    DATABASE_URL: str = "sqlite:///./data/app.db"
    REDIS_URL: str = "redis://localhost:6379/0"

    JWT_SECRET: str = "super-secret-jwt-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    ADMIN_EMAIL: str = "admin@example.com"
    ADMIN_PASSWORD: str = "AdminPassword123!"

    MEDIA_DIR: Path = Path("./media")
    VIDEOS_DIR: Path = Path("./media/videos")
    AUDIO_DIR: Path = Path("./media/audio")

    CORS_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @property
    def cors_origins_list(self) -> list[str]:
        if self.CORS_ORIGINS.strip() == "*":
            return ["*"]
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

settings = Settings()
