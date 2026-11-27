"""Add user_skills.note: the user's optional note when hiding or disputing a skill (M4.5).

Revision ID: d8e2f4a61b37
Revises: c5d1e7f20a94
Create Date: 2026-11-27 10:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "d8e2f4a61b37"
down_revision: str | Sequence[str] | None = "c5d1e7f20a94"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("user_skills", sa.Column("note", sa.Text(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("user_skills", "note")
