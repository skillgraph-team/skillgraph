"""Tests for app/config.py: settings come from environment variables."""

import pytest
from pydantic import ValidationError

from app.config import Settings


def test_defaults_without_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("APP_ENV", raising=False)

    settings = Settings(_env_file=None)

    assert settings.app_env == "dev"


def test_reads_environment_variable(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APP_ENV", "test")

    settings = Settings(_env_file=None)

    assert settings.app_env == "test"


def test_rejects_unknown_environment_name(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APP_ENV", "staging")

    with pytest.raises(ValidationError):
        Settings(_env_file=None)


def test_test_database_defaults_to_separate_database(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("TEST_DATABASE_URL", raising=False)

    settings = Settings(_env_file=None)

    assert settings.test_database_url != settings.database_url
    assert settings.test_database_url.endswith("_test")


def test_rejects_test_database_equal_to_dev_database(monkeypatch: pytest.MonkeyPatch) -> None:
    url = "postgresql+psycopg://u:p@localhost:5432/skillgraph"
    monkeypatch.setenv("DATABASE_URL", url)
    monkeypatch.setenv("TEST_DATABASE_URL", url)

    with pytest.raises(ValidationError):
        Settings(_env_file=None)
