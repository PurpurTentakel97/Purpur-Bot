"""counter

Revision ID: 3fc61638387e
Revises: 44a32ead3a7c
Create Date: 2026-01-06 22:05:15.299487

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "3fc61638387e"
down_revision: str | Sequence[str] | None = "44a32ead3a7c"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "counter",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("bot_id", sa.Integer, nullable=False),
        sa.Column("name", sa.String, nullable=False),
        sa.Column("count", sa.Integer, nullable=False, server_default="0"),
        sa.ForeignKeyConstraint(["bot_id"], ["bot_config.id"], ondelete="CASCADE"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("counter")
