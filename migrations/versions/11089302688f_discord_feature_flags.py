"""discord feature flags

Revision ID: 11089302688f
Revises: edb2c6a0aa0a
Create Date: 2026-01-19 23:15:05.460965

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "11089302688f"
down_revision: str | Sequence[str] | None = "edb2c6a0aa0a"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "discord_feature_flags",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("bot_id", sa.Integer(), nullable=False),
        sa.Column("server_id", sa.Integer(), nullable=False),
        sa.Column("can_commands", sa.Boolean(), nullable=False, server_default="True"),
        sa.Column("can_alias", sa.Boolean(), nullable=False, server_default="True"),
        sa.ForeignKeyConstraint(["bot_id"], ["bot_config.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["server_id"], ["bot_discord_lookup.server_id"], ondelete="CASCADE"),
        sa.UniqueConstraint("bot_id", "server_id", name="unique_discord_bot_id"),
    )


def downgrade() -> None:
    op.drop_table("discord_feature_flags")
