"""unique counter

Revision ID: 840835c33715
Revises: ed8e46f3c69a
Create Date: 2026-01-19 20:13:44.705465

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "840835c33715"
down_revision: str | Sequence[str] | None = "ed8e46f3c69a"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("counter") as batch_op:
        batch_op.create_unique_constraint("unique_counter", ["bot_id", "name"])


def downgrade() -> None:
    with op.batch_alter_table("counter") as batch_op:
        batch_op.drop_constraint("unique_counter", type_="unique")
