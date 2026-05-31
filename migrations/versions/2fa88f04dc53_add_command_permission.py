"""command permission

Revision ID: 2fa88f04dc53
Revises: ec255c4d579a
Create Date: 2026-05-31 14:37:16.028431

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

from bot.core.types.permission_level import PermissionLevel

# revision identifiers, used by Alembic.
revision: str = "2fa88f04dc53"
down_revision: str | Sequence[str] | None = "ec255c4d579a"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "basic_commands",
        sa.Column("permission_level", sa.Integer(), nullable=False, server_default=str(int(PermissionLevel.USER))),
    )


def downgrade() -> None:
    op.drop_column("basic_commands", "permission_level")
