"""quote feature flags

Revision ID: ec255c4d579a
Revises: 59aca9df4ea2
Create Date: 2026-03-21 14:54:49.685412

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "ec255c4d579a"
down_revision: str | Sequence[str] | None = "59aca9df4ea2"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "discord_feature_flags",
        sa.Column("can_quotes", sa.Boolean(), nullable=False, server_default=sa.text("1")),
    )
    (
        op.add_column(
            "twitch_feature_flags",
            sa.Column("can_quotes", sa.Boolean(), nullable=False, server_default=sa.text("1")),
        )
    )


def downgrade() -> None:
    op.drop_column("discord_feature_flags", "can_quotes")
    op.drop_column("twitch_feature_flags", "can_quotes")
