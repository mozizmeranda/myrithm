from pathlib import Path
from typing import Literal
from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_ENV: Literal["development", "test", "production"] = "development"
    APP_TIMEZONE: str = "Asia/Tashkent"

    DATABASE_URL: str = "sqlite:///./data/app.db"
    REDIS_URL: str = "redis://localhost:6379/0"

    JWT_SECRET_KEY: str = Field(
        default="super-secret-jwt-key-change-in-production",
        validation_alias="JWT_SECRET_KEY",
        alias="JWT_SECRET"
    )
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
    def JWT_SECRET(self) -> str:
        return self.JWT_SECRET_KEY

    @property
    def cors_origins_list(self) -> list[str]:
        if self.CORS_ORIGINS.strip() == "*":
            return ["*"]
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    @model_validator(mode="after")
    def validate_production_settings(self) -> "Settings":
        if self.APP_ENV == "production":
            default_secret = "super-secret-jwt-key-change-in-production"
            if self.JWT_SECRET_KEY == default_secret or len(self.JWT_SECRET_KEY) < 32:
                raise ValueError("Production mode requires a strong JWT_SECRET_KEY (at least 32 characters, non-default)")
            if self.ADMIN_PASSWORD == "AdminPassword123!":
                raise ValueError("Production mode requires a non-default ADMIN_PASSWORD")
        return self

settings = Settings()

