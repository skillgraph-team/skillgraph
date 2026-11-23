"""initial empty

Revision ID: 6b7e9a43c1b8
Revises:
Create Date: 2026-11-23 15:35:42.907104

"""

from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = "6b7e9a43c1b8"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
