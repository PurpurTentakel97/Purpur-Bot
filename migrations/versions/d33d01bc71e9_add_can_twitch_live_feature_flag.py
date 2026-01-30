"""add can_twitch_live feature flag

Revision ID: d33d01bc71e9
Revises: b81f56d4da05
Create Date: 2026-01-30 23:36:32.273900

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "d33d01bc71e9"
down_revision: str | Sequence[str] | None = "b81f56d4da05"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "discord_feature_flags",
        sa.Column("can_twitch_live", sa.Boolean(), nullable=False, server_default=sa.text("1")),
    )
    op.add_column(
        "twitch_feature_flags", sa.Column("can_twitch_live", sa.Boolean(), nullable=False, server_default=sa.text("0"))
    )


def downgrade() -> None:
    op.drop_column("discord_feature_flags", "can_twitch_live")
    op.drop_column("twitch_feature_flags", "can_twitch_live")
