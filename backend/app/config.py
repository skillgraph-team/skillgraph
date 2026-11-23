"""Settings for the backend, read from environment variables (and a local `.env` file).

Add a field here for each new setting, with a safe default for local development,
and add the same name to `.env.example`. Never put real secrets in defaults.
"""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# The repo-root .env (README: `cp .env.example .env`), wherever the server is started from.
ENV_FILE = Path(__file__).resolve().parents[2] / ".env"

# Matches the local database in docker-compose.yml. Local-only values, not secrets.
_LOCAL_DB = "postgresql+psycopg://skillgraph:skillgraph@localhost:5432"


class Settings(BaseSettings):
    # extra="ignore": .env also holds settings for other tools (e.g. Docker), which is fine.
    model_config = SettingsConfigDict(env_file=ENV_FILE, extra="ignore")

    app_env: Literal["dev", "test", "prod"] = "dev"
    database_url: str = f"{_LOCAL_DB}/skillgraph"
    # Tests only ever use this one, so running them never touches your development data.
    test_database_url: str = f"{_LOCAL_DB}/skillgraph_test"

    @model_validator(mode="after")
    def _test_database_is_separate(self) -> "Settings":
        if self.test_database_url == self.database_url:
            raise ValueError("TEST_DATABASE_URL must differ from DATABASE_URL")
        return self


@lru_cache
def get_settings() -> Settings:
    """The settings, read once and then reused."""
    return Settings()
