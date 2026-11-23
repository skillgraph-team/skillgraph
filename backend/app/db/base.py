"""The base class every database model (table) inherits from.

Alembic reads `Base.metadata` to see which tables exist in the code, so a new model
must be imported in `app/db/models/__init__.py` to be picked up by
`alembic revision --autogenerate`.

The naming convention gives every index and constraint a predictable name
(e.g. `ck_evidence_type`), so migrations can find them again to change or drop them.
"""

from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase

NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_N_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_N_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)
