"""Settings for the backend, read from environment variables (and a local `.env` file).

Add a field here for each new setting, with a safe default for local development,
and add the same name to `.env.example`. Never put real secrets in defaults.
"""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

# The repo-root .env (README: `cp .env.example .env`), wherever the server is started from.
ENV_FILE = Path(__file__).resolve().parents[2] / ".env"


class Settings(BaseSettings):
    # extra="ignore": .env also holds settings for other tools (e.g. Docker), which is fine.
    model_config = SettingsConfigDict(env_file=ENV_FILE, extra="ignore")

    app_env: Literal["dev", "test", "prod"] = "dev"


@lru_cache
def get_settings() -> Settings:
    """The settings, read once and then reused."""
    return Settings()
