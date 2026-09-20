from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str = "sqlite:///./trip_planner.db"
    weather_api_key: str = ""
    weather_timeout_seconds: float = 4.0
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"


settings = Settings()
