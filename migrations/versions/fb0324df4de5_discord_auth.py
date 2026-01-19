"""discord_auth

Revision ID: fb0324df4de5
Revises: db16b70e1f62
Create Date: 2026-01-04 21:16:03.719508

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "fb0324df4de5"
down_revision: str | Sequence[str] | None = "db16b70e1f62"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "discord_auth",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("discord_id", sa.String, nullable=False),
        sa.Column("access_token", sa.String, nullable=False),
        sa.Column("refresh_token", sa.String, nullable=False),
        sa.Column("expires_at", sa.Integer, nullable=False),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("discord_auth")
