"""add twitch event hub active bool

Revision ID: 33e374c522b2
Revises: d33d01bc71e9
Create Date: 2026-01-31 20:39:22.419716

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "33e374c522b2"
down_revision: str | Sequence[str] | None = "d33d01bc71e9"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("twitch_event_hub", sa.Column("enabled", sa.Boolean(), nullable=False, server_default="1"))


def downgrade() -> None:
    op.drop_column("twitch_event_hub", "enabled")
