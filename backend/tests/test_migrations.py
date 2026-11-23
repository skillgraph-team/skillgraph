"""Tests for migrations/: every migration applies and rolls back cleanly on the test database,
and the migrations create exactly the tables the models in app/db/models describe."""

from alembic import command
from alembic.autogenerate import compare_metadata
from alembic.config import Config
from alembic.migration import MigrationContext
from sqlalchemy import Engine, inspect

from app.db.models import Base

# The tables of schema v1 (docs/design/schema.md).
SCHEMA_V1_TABLES = {
    "users",
    "profiles",
    "education",
    "experience",
    "manual_projects",
    "sources",
    "evidence",
    "skills",
    "skill_aliases",
    "skill_relations",
    "user_skills",
    "user_skill_evidence",
    "opportunities",
    "opportunity_requirements",
    "matches",
    "agent_runs",
    "agent_messages",
}


def test_upgrade_then_downgrade_then_upgrade(alembic_config: Config, test_engine: Engine) -> None:
    command.downgrade(alembic_config, "base")
    assert set(inspect(test_engine).get_table_names()) == {"alembic_version"}

    command.upgrade(alembic_config, "head")

    assert set(inspect(test_engine).get_table_names()) == SCHEMA_V1_TABLES | {"alembic_version"}


def test_models_match_the_migrations(test_engine: Engine) -> None:
    """If this fails, a model changed without a migration: run `alembic revision --autogenerate`."""
    with test_engine.connect() as connection:
        differences = compare_metadata(MigrationContext.configure(connection), Base.metadata)

    assert differences == []
