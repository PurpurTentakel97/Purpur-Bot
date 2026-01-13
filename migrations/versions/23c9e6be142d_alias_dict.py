"""alias-dict

Revision ID: 23c9e6be142d
Revises: 2b3134877aae
Create Date: 2026-01-11 23:21:03.333810

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "23c9e6be142d"
down_revision: str | Sequence[str] | None = "2b3134877aae"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "alias_dict",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("bot_id", sa.Integer, nullable=False),
        sa.Column("alias", sa.String, nullable=False),
        sa.Column("explanation", sa.String, nullable=False),
        sa.ForeignKeyConstraint(["bot_id"], ["bot_config.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("bot_id", "alias", name="unique_alias_for_bot"),
    )


def downgrade() -> None:
    op.drop_table("alias_dict")
