"""basic_commands

Revision ID: db16b70e1f62
Revises: dfed1499eccd
Create Date: 2026-01-04 19:54:39.469731

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "db16b70e1f62"
down_revision: str | Sequence[str] | None = "dfed1499eccd"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "basic_commands",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("bot_id", sa.Integer, nullable=False),
        sa.Column("command", sa.String, nullable=False),
        sa.Column("message", sa.String, nullable=False),
        sa.ForeignKeyConstraint(["bot_id"], ["bot_config.id"]),
    )
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
