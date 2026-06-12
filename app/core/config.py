from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Server
    PORT: int = 8000
    ENVIRONMENT: str = "development"

    # Database
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "task_manager_db"
    DB_USER: str = "postgres"
    DB_PASSWORD: str

    # JWT
    JWT_SECRET: str = "changeme"
    JWT_EXPIRES_IN: int = 1          # days
    JWT_REFRESH_SECRET: str = "changeme-refresh"
    JWT_REFRESH_EXPIRES_IN: int = 7  # days

    # Rate limiting
    RATE_LIMIT_MAX: int = 100

    # Feature flags
    ALLOW_ADMIN_SIGNUP: bool = False

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    @property
    def sync_database_url(self) -> str:
        """Used by Alembic (synchronous)."""
        return (
            f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )


settings = Settings()
