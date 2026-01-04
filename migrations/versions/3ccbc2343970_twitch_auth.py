"""twitch_auth

Revision ID: 3ccbc2343970
Revises:
Create Date: 2026-01-03 20:17:49.352431

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "3ccbc2343970"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "twitch_auth",
        sa.Column("twitch_id", sa.String, nullable=False, primary_key=True),
        sa.Column("access_token", sa.String, nullable=False),
        sa.Column("refresh_token", sa.String, nullable=False),
        sa.Column("expires_at", sa.Integer, nullable=False),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("twitch_auth")
