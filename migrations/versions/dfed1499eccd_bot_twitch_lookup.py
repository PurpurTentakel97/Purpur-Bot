"""bot twitch lookup

Revision ID: dfed1499eccd
Revises: a6016acbb591
Create Date: 2026-01-04 18:23:33.556377

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "dfed1499eccd"
down_revision: str | Sequence[str] | None = "a6016acbb591"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "bot_twitch_lookup",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("bot_id", sa.Integer, nullable=False),
        sa.Column("channel_name", sa.String, nullable=False),
        sa.ForeignKeyConstraint(["bot_id"], ["bot_config.id"], ondelete="CASCADE"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("bot_twitch_lookup")
    pass
