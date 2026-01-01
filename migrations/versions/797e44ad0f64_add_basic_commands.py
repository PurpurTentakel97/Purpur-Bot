"""add basic commands

Revision ID: 797e44ad0f64
Revises:
Create Date: 2025-12-31 21:56:05.525401

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "797e44ad0f64"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "basic_commands",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String, nullable=False, primary_key=True),
        sa.Column("message", sa.String, nullable=False),
    )


def downgrade() -> None:
    op.drop_table("basic_commands")
