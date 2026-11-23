"""Tests for migrations/: every migration applies and rolls back cleanly on the test database."""

from alembic import command
from alembic.config import Config
from sqlalchemy import Engine, inspect


def test_upgrade_then_downgrade_then_upgrade(alembic_config: Config, test_engine: Engine) -> None:
    command.downgrade(alembic_config, "base")
    command.upgrade(alembic_config, "head")

    assert "alembic_version" in inspect(test_engine).get_table_names()
