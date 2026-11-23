"""How Alembic connects to the database when it runs migrations.

- Which database: `sqlalchemy.url` if it is set (the tests set it to the test database),
  otherwise DATABASE_URL from app/config.py.
- Which tables the code defines: `Base.metadata`, used by `alembic revision --autogenerate`.

Usage (from backend/): `uv run alembic upgrade head` to apply all migrations;
`uv run alembic revision --autogenerate -m "<what changed>"` to create a new one.
Never edit a migration that has been merged; add a new one instead.
"""

from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine, pool

from app.config import get_settings
from app.db.models import Base  # imports every model, so autogenerate sees all tables

config = context.config
if config.config_file_name is not None:
    # disable_existing_loggers=False: keep the app's own loggers working (e.g. during tests).
    fileConfig(config.config_file_name, disable_existing_loggers=False)

target_metadata = Base.metadata


def database_url() -> str:
    return config.get_main_option("sqlalchemy.url") or get_settings().database_url


def run_migrations_offline() -> None:
    """`alembic upgrade head --sql`: print the SQL instead of running it."""
    context.configure(url=database_url(), target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Connect to the database and apply the migrations."""
    engine = create_engine(database_url(), poolclass=pool.NullPool)
    with engine.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()
    engine.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
