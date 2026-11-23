"""The base class every database model (table) inherits from.

Alembic reads `Base.metadata` to see which tables exist in the code, so a new model
must be imported in `app/db/models/__init__.py` (from M2.4) to be picked up by
`alembic revision --autogenerate`.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
