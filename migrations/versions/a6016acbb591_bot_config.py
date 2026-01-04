"""bot config

Revision ID: a6016acbb591
Revises: 3ccbc2343970
Create Date: 2026-01-04 14:01:50.672120

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a6016acbb591"
down_revision: str | Sequence[str] | None = "3ccbc2343970"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "bot_config",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("twitch_user_id", sa.Integer, nullable=False),
        sa.Column("name", sa.String, nullable=False, default="new bot"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("bot_config")
