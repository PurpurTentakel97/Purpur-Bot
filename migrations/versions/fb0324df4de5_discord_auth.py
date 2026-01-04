"""discord_auth

Revision ID: fb0324df4de5
Revises: db16b70e1f62
Create Date: 2026-01-04 21:16:03.719508

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fb0324df4de5'
down_revision: Union[str, Sequence[str], None] = 'db16b70e1f62'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "discord_auth",
        sa.Column("discord_id", sa.String, nullable=False, primary_key=True),
        sa.Column("access_token", sa.String, nullable=False),
        sa.Column("refresh_token", sa.String, nullable=False),
        sa.Column("expires_at", sa.Integer, nullable=False),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("discord_auth")
