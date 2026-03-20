"""quotes

Revision ID: 59aca9df4ea2
Revises: 80a946888ba9
Create Date: 2026-03-17 21:44:28.410663

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "59aca9df4ea2"
down_revision: str | Sequence[str] | None = "80a946888ba9"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "quotes",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("bot_id", sa.Integer, nullable=False),
        sa.Column("discord_user_id", sa.Integer),
        sa.Column("twitch_user_id", sa.String),
        sa.Column("timestamp", sa.Integer, nullable=False),
        sa.Column("quote", sa.String, nullable=False),
        sa.ForeignKeyConstraint(["bot_id"], ["bot_config.id"], ondelete="CASCADE"),
    )


def downgrade() -> None:
    op.drop_table("quotes")
