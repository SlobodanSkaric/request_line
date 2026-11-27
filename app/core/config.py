from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL

BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "RequestLine"
    debug: bool = False

    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_user: str
    postgres_password: str
    postgres_db: str

    db_pool_size: int = 5
    db_max_overflow: int = 10
    db_echo: bool = False

    secret_key: str
    access_token_expire_minutes: int = 5
    refresh_token_expire_minutes: int = 45
    jwt_algorithm: str = "HS256"

    def _database_url(self, driver: str) -> URL:
        return URL.create(
            drivername=driver,
            username=self.postgres_user,
            password=self.postgres_password,
            host=self.postgres_host,
            port=self.postgres_port,
            database=self.postgres_db,
        )

    @property
    def async_database_url(self) -> URL:
        return self._database_url("postgresql+asyncpg")

    @property
    def sync_database_url(self) -> URL:
        return self._database_url("postgresql+psycopg2")


@lru_cache
def get_settings() -> Settings:
    return Settings()
