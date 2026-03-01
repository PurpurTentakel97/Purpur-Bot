"""add_twitch_broadcast_auth

Revision ID: 80a946888ba9
Revises: 33e374c522b2
Create Date: 2026-03-01 18:21:50.629310

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '80a946888ba9'
down_revision: Union[str, Sequence[str], None] = '33e374c522b2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "twitch_broadcast_auth",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("bot_id", sa.Integer, nullable=False),
        sa.Column("channel_name", sa.String, nullable=False),
        sa.Column("twitch_user_id", sa.String, nullable=False),
        sa.Column("access_token", sa.String, nullable=False),
        sa.Column("refresh_token", sa.String, nullable=False),
        sa.Column("expires_at", sa.Integer, nullable=False),
        sa.ForeignKeyConstraint(["bot_id"], ["bot_config.id"], ondelete="CASCADE"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("twitch_broadcast_auth")
