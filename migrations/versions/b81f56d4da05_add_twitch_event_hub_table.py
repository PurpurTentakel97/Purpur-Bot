"""add twitch_event_hub table

Revision ID: b81f56d4da05
Revises: 368b525e0924
Create Date: 2026-01-28 20:32:20.716986

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b81f56d4da05"
down_revision: str | Sequence[str] | None = "368b525e0924"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "twitch_event_hub",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("bot_id", sa.Integer(), nullable=False),
        sa.Column("broadcaster_id", sa.String(), nullable=False),
        sa.Column("message", sa.String(), nullable=False),
        sa.Column("server_id", sa.BigInteger(), nullable=False),
        sa.Column("channel_id", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(["bot_id"], ["bot_config.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("server_id", "broadcaster_id", name="uq_twitch_event_hub_server_broadcaster"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("twitch_event_hub")
