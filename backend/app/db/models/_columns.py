"""Column and constraint helpers shared by all models, so every table looks the same.

- `uuid_pk`: a UUID id, created in Python (so it's known before saving) with a
  database default as a fallback for raw SQL (D-019).
- `created_at` / `updated_at`: timestamps with time zone, filled by the database.
- `one_of`: a CHECK constraint that a text column holds one of the allowed values.
- `user_ref`: the link to `users.id` that every personal-data table has; deleting the
  user deletes the row (ON DELETE CASCADE).
"""

import uuid
from datetime import datetime
from typing import Annotated

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, func, text
from sqlalchemy.orm import mapped_column

from app.db.values import values

uuid_pk = Annotated[
    uuid.UUID,
    mapped_column(primary_key=True, default=uuid.uuid4, server_default=text("gen_random_uuid()")),
]
created_at = Annotated[datetime, mapped_column(DateTime(timezone=True), server_default=func.now())]
updated_at = Annotated[
    datetime,
    mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now()),
]


user_ref = Annotated[
    uuid.UUID, mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
]
"""`user_id` column type: who the row belongs to. Deleting the user deletes the row.
Use `Mapped[user_ref | None]` where the user is optional."""


def one_of(column: str, literal: object, *, nullable: bool = False) -> CheckConstraint:
    """CHECK that `column` is one of the values of `literal` (see app/db/values.py)."""
    allowed = ", ".join(f"'{value}'" for value in values(literal))
    condition = f"{column} IN ({allowed})"
    if nullable:
        condition = f"{column} IS NULL OR {condition}"
    return CheckConstraint(condition, name=column)
