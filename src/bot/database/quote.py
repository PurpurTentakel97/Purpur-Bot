from datetime import UTC
from datetime import datetime
from typing import Final
from typing import Optional

from bot.core.types.programm_parts import PROGRAMM_PARTS
from bot.core.types.result import Result
from bot.database.types.fields import FIELD_BOT_ID
from bot.database.types.fields import FIELD_DISCORD_USER_ID
from bot.database.types.fields import FIELD_ID
from bot.database.types.fields import FIELD_QUOTE_MESSAGE
from bot.database.types.fields import FIELD_TIMESTAMP
from bot.database.types.fields import FIELD_TWITCH_USER_ID
from bot.database.types.fields import TABLE_QUOTE_NAME
from bot.database.types.quote import Quote


def select_quote_by_id(quote_id: int) -> Result[Quote]:
    return PROGRAMM_PARTS.database.select_one(table_name=TABLE_QUOTE_NAME, where={FIELD_ID: quote_id}, type_=Quote)


def select_quote_by_discord_id(*, bot_id: int, discord_id: int) -> Result[list[Quote]]:
    return PROGRAMM_PARTS.database.select_all(
        table_name=TABLE_QUOTE_NAME,
        where={FIELD_BOT_ID: bot_id, FIELD_DISCORD_USER_ID: discord_id},
        type_=Quote,
    )


def select_quote_by_twitch_id(bot_id: int, twitch_id: str) -> Result[list[Quote]]:
    return PROGRAMM_PARTS.database.select_all(
        table_name=TABLE_QUOTE_NAME,
        where={FIELD_BOT_ID: bot_id, FIELD_TWITCH_USER_ID: twitch_id},
        type_=Quote,
    )


def insert_quote(bot_id: int, discord_id: Optional[int], twitch_id: Optional[str], quote: str) -> Result[int]:
    timestamp: Final = datetime.now(UTC)
    return PROGRAMM_PARTS.database.insert(
        table_name=TABLE_QUOTE_NAME,
        data={
            FIELD_BOT_ID: bot_id,
            FIELD_DISCORD_USER_ID: discord_id,
            FIELD_TWITCH_USER_ID: twitch_id,
            FIELD_QUOTE_MESSAGE: quote,
            FIELD_TIMESTAMP: timestamp,
        },
    )


def update_quote(quote_id: int, quote: str) -> Result[None]:
    return PROGRAMM_PARTS.database.update(
        table_name=TABLE_QUOTE_NAME, data={FIELD_QUOTE_MESSAGE: quote}, where={FIELD_ID: quote_id}
    )


def delete_quote(quote_id: int) -> Result[None]:
    return PROGRAMM_PARTS.database.delete(table_name=TABLE_QUOTE_NAME, where={FIELD_ID: quote_id})
