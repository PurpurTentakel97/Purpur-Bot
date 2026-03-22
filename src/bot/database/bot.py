from typing import Any

from bot.core.types.programm_parts import PROGRAMM_PARTS
from bot.core.types.result import Result
from bot.database.types.bot_config import BotConfigDB
from bot.database.types.fields import FIELD_ENABLED
from bot.database.types.fields import FIELD_ID
from bot.database.types.fields import FIELD_TWITCH_USER_ID
from bot.database.types.fields import TABLE_BOT_CONFIG_NAME


def select_all_active_bots() -> Result[list[BotConfigDB]]:
    return PROGRAMM_PARTS.database.select_all(
        table_name=TABLE_BOT_CONFIG_NAME, where={FIELD_ENABLED: True}, type_=BotConfigDB
    )


def select_bot(bot_id: int) -> Result[BotConfigDB]:
    return PROGRAMM_PARTS.database.select_one(
        table_name=TABLE_BOT_CONFIG_NAME, where={FIELD_ID: bot_id}, type_=BotConfigDB
    )


def select_bots_by_twitch_id(twitch_user_id: str) -> Result[list[BotConfigDB]]:
    return PROGRAMM_PARTS.database.select_all(
        table_name=TABLE_BOT_CONFIG_NAME, where={FIELD_TWITCH_USER_ID: twitch_user_id}, type_=BotConfigDB
    )


def insert_bot(twitch_user_id: str) -> Result[int]:
    return PROGRAMM_PARTS.database.insert(table_name=TABLE_BOT_CONFIG_NAME, data={FIELD_TWITCH_USER_ID: twitch_user_id})


def update_bot(bot_id: int, data: dict[str, Any]) -> Result[None]:
    return PROGRAMM_PARTS.database.update(table_name=TABLE_BOT_CONFIG_NAME, where={FIELD_ID: bot_id}, data=data)


def delete_bot(bot_id: int) -> Result[None]:
    return PROGRAMM_PARTS.database.delete(table_name=TABLE_BOT_CONFIG_NAME, where={FIELD_ID: bot_id})
