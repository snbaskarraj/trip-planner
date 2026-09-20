from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    database_url: str = Field(
        default="sqlite:///./trip_planner.db",
        validation_alias=AliasChoices("DATABASE_URL", "database_url"),
    )
    weather_api_key: str = ""
    weather_timeout_seconds: float = 4.0
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"


settings = Settings()
