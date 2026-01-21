"""twitch broadcast message

Revision ID: 597859e41b11
Revises: 11089302688f
Create Date: 2026-01-20 22:33:58.040943

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "597859e41b11"
down_revision: str | Sequence[str] | None = "11089302688f"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "twitch_broadcast_message",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("bot_id", sa.Integer, nullable=False),
        sa.Column("channel_name", sa.String, nullable=False),
        sa.Column("message", sa.String, nullable=False),
        sa.Column("interval_in_minutes", sa.Integer, nullable=False),
        sa.ForeignKeyConstraint(["bot_id"], ["bot_config.id"], ondelete="CASCADE"),
    )


def downgrade() -> None:
    op.drop_table("twitch_broadcast_message")
