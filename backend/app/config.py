from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = "postgresql+psycopg2://req2veri:req2veri@localhost:5432/req2veri"
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    jwt_secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24
    reset_db_user: str = ""
    reset_db_password: str = ""
    backup_dir: str = "backups"
    app_log_file: str = "logs/app.log"
    app_log_level: str = "INFO"
    app_log_max_bytes: int = 5 * 1024 * 1024
    app_log_backup_count: int = 5


@lru_cache
def get_settings() -> Settings:
    return Settings()
