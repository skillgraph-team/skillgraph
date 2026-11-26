"""Settings for the backend, read from environment variables (and a local `.env` file).

Add a field here for each new setting, with a safe default for local development,
and add the same name to `.env.example`. Never put real secrets in defaults.
"""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parents[1]

# The repo-root .env (README: `cp .env.example .env`), wherever the server is started from.
ENV_FILE = Path(__file__).resolve().parents[2] / ".env"

# Matches the local database in docker-compose.yml. Local-only values, not secrets.
_LOCAL_DB = "postgresql+psycopg://skillgraph:skillgraph@localhost:5432"

# Signs login tokens. Fine for local development only: production must set SECRET_KEY.
_DEV_SECRET_KEY = "dev-only-insecure-secret-key-do-not-use-in-production"
# Placeholder values that must never sign real tokens.
_PLACEHOLDER_SECRET_KEYS = {_DEV_SECRET_KEY, "change-me-to-a-long-random-string"}


class Settings(BaseSettings):
    # extra="ignore": .env also holds settings for other tools (e.g. Docker), which is fine.
    model_config = SettingsConfigDict(env_file=ENV_FILE, extra="ignore")

    app_env: Literal["dev", "test", "prod"] = "dev"
    database_url: str = f"{_LOCAL_DB}/skillgraph"
    # Tests only ever use this one, so running them never touches your development data.
    test_database_url: str = f"{_LOCAL_DB}/skillgraph_test"

    # Login (D-015): a signed token in an HttpOnly cookie.
    secret_key: str = Field(default=_DEV_SECRET_KEY, min_length=32)
    login_lifetime_hours: int = Field(default=24, ge=1)
    # True when the site is served over HTTPS (production): the browser then only sends
    # the login cookie over HTTPS. False for http://localhost.
    cookie_secure: bool = False

    # Uploaded files (M3.5). Kept outside any folder the web server publishes; the
    # default `backend/storage/` is git-ignored.
    upload_dir: Path = BACKEND_DIR / "storage" / "uploads"
    # Largest CV file accepted, in bytes (default 5 MB).
    cv_max_bytes: int = Field(default=5 * 1024 * 1024, ge=1)

    # GitHub import (M3.6, D-009: public data by username, no user login).
    # Optional server token: raises GitHub's limit from 60 to 5000 requests an hour.
    # Empty means no token. Never logged, never stored in the cache.
    github_token: SecretStr | None = None
    github_api_url: str = "https://api.github.com"
    # Saved GitHub answers (public data only), reused for `github_cache_seconds`.
    github_cache_dir: Path = BACKEND_DIR / "storage" / "github_cache"
    github_cache_seconds: int = Field(default=3600, ge=0)
    # Most recently pushed repos imported per user. Each costs up to ~6 requests, so 10
    # fits in the 60 an hour allowed without a token; raise it when GITHUB_TOKEN is set.
    github_max_repos: int = Field(default=10, ge=1, le=100)

    @model_validator(mode="after")
    def _test_database_is_separate(self) -> "Settings":
        if self.test_database_url == self.database_url:
            raise ValueError("TEST_DATABASE_URL must differ from DATABASE_URL")
        return self

    @model_validator(mode="after")
    def _real_secret_in_production(self) -> "Settings":
        if self.app_env == "prod" and self.secret_key in _PLACEHOLDER_SECRET_KEYS:
            raise ValueError("set SECRET_KEY to a long random value in production")
        return self


@lru_cache
def get_settings() -> Settings:
    """The settings, read once and then reused."""
    return Settings()
