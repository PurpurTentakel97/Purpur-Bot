"""twitch feature flags

Revision ID: edb2c6a0aa0a
Revises: 840835c33715
Create Date: 2026-01-19 22:23:56.534459

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "edb2c6a0aa0a"
down_revision: str | Sequence[str] | None = "840835c33715"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "twitch_feature_flags",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("bot_id", sa.Integer(), nullable=False),
        sa.Column("channel_name", sa.String(), nullable=False),
        sa.Column("can_commands", sa.Boolean(), nullable=False, server_default="True"),
        sa.Column("can_alias", sa.Boolean(), nullable=False, server_default="True"),
        sa.ForeignKeyConstraint(["bot_id"], ["bot_config.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("bot_id", "channel_name", name="unique_twitch_bot_id"),
    )


def downgrade() -> None:
    op.drop_table("twitch_feature_flags")
