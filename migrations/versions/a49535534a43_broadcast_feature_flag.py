"""broadcast feature flag

Revision ID: a49535534a43
Revises: 597859e41b11
Create Date: 2026-01-21 01:04:22.072501

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a49535534a43"
down_revision: str | Sequence[str] | None = "597859e41b11"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "twitch_feature_flags", sa.Column("can_broadcast", sa.Boolean(), nullable=False, server_default="True")
    )
    op.add_column(
        "discord_feature_flags", sa.Column("can_broadcast", sa.Boolean(), nullable=False, server_default="False")
    )


def downgrade() -> None:
    op.drop_column("twitch_feature_flags", "can_broadcast")
    op.drop_column("discord_feature_flags", "can_broadcast")
