"""bot discord lookup

Revision ID: 44a32ead3a7c
Revises: fb0324df4de5
Create Date: 2026-01-05 20:58:08.180514

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "44a32ead3a7c"
down_revision: str | Sequence[str] | None = "fb0324df4de5"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "bot_discord_lookup",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("bot_id", sa.Integer, nullable=False),
        sa.Column("server_id", sa.Integer, nullable=False),
        sa.Column("server_name", sa.String, nullable=False),
        sa.ForeignKeyConstraint(["bot_id"], ["bot_config.id"]),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("bot_discord_lookup")
