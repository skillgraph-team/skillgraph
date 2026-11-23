"""Connection to PostgreSQL and the per-request database session.

Endpoints get a session by declaring a parameter `session: DbSession`. Tests replace
`get_session` with a session on the test database (see `tests/conftest.py`).
"""

from collections.abc import Iterator
from typing import Annotated

from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import get_settings

# pool_pre_ping: check a pooled connection still works before using it.
engine = create_engine(get_settings().database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine)


def get_session() -> Iterator[Session]:
    """One session per request, always closed afterwards."""
    with SessionLocal() as session:
        yield session


# Use as an endpoint parameter type: `def endpoint(session: DbSession) -> ...`
DbSession = Annotated[Session, Depends(get_session)]
