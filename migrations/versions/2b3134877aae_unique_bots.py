"""unique bots

Revision ID: 2b3134877aae
Revises: 3fc61638387e
Create Date: 2026-01-11 22:47:25.462806

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "2b3134877aae"
down_revision: str | Sequence[str] | None = "3fc61638387e"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("bot_discord_lookup") as batch_op:
        batch_op.create_unique_constraint("unique_discord_bot_id", ["server_id"])

    with op.batch_alter_table("bot_twitch_lookup") as batch_op:
        batch_op.create_unique_constraint("unique_twitch_bot_id", ["channel_name"])


def downgrade() -> None:
    with op.batch_alter_table("bot_discord_lookup") as batch_op:
        batch_op.drop_constraint("unique_discord_bot_id", type_="unique")

    with op.batch_alter_table("bot_twitch_lookup") as batch_op:
        batch_op.drop_constraint("unique_twitch_bot_id", type_="unique")
