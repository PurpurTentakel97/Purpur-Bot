"""unique commands

Revision ID: ed8e46f3c69a
Revises: 23c9e6be142d
Create Date: 2026-01-19 19:58:35.041902

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "ed8e46f3c69a"
down_revision: str | Sequence[str] | None = "23c9e6be142d"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("basic_commands") as batch_op:
        batch_op.create_unique_constraint("unique_command", ["bot_id", "command"])


def downgrade() -> None:
    with op.batch_alter_table("basic_commands") as batch_op:
        batch_op.drop_constraint("unique_command", type_="unique")
