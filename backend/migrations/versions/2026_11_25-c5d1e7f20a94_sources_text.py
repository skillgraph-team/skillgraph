"""Add sources.text: the plain text read from an uploaded CV (M3.5).

Revision ID: c5d1e7f20a94
Revises: a3c8991e349d
Create Date: 2026-11-25 10:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c5d1e7f20a94"
down_revision: str | Sequence[str] | None = "a3c8991e349d"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("sources", sa.Column("text", sa.Text(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("sources", "text")
