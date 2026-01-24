"""add single enable bools

Revision ID: 368b525e0924
Revises: a49535534a43
Create Date: 2026-01-21 23:33:32.887240

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "368b525e0924"
down_revision: str | Sequence[str] | None = "a49535534a43"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("alias_dict", sa.Column("enabled", sa.Boolean(), nullable=False, server_default="True"))
    op.add_column("basic_commands", sa.Column("enabled", sa.Boolean(), nullable=False, server_default="True"))
    op.add_column("twitch_broadcast_message", sa.Column("enabled", sa.Boolean(), nullable=False, server_default="True"))
    op.add_column("bot_twitch_lookup", sa.Column("enabled", sa.Boolean(), nullable=False, server_default="True"))
    op.add_column("bot_discord_lookup", sa.Column("enabled", sa.Boolean(), nullable=False, server_default="True"))
    op.add_column("bot_config", sa.Column("enabled", sa.Boolean(), nullable=False, server_default="True"))


def downgrade() -> None:
    op.drop_column("twitch_broadcast_message", "enabled")
    op.drop_column("basic_commands", "enabled")
    op.drop_column("alias_dict", "enabled")
    op.drop_column("bot_discord_lookup", "enabled")
    op.drop_column("bot_twitch_lookup", "enabled")
    op.drop_column("bot_config", "enabled")
