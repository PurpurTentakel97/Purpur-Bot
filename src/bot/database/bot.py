from typing import Any
from typing import Optional

from bot.core.types.programm_parts import PROGRAMM_PARTS
from bot.database.types.bot_config import BotConfigDB

TABLE_NAME = "bot_config"
FIELD_NAME = "name"


def select_bot(bot_id: int) -> Optional[BotConfigDB]:
    return PROGRAMM_PARTS.database.select_one(table_name=TABLE_NAME, where={"id": bot_id}, type_=BotConfigDB)


def select_bots_by_twitch_id(twitch_user_id: str) -> list[BotConfigDB]:
    return PROGRAMM_PARTS.database.select_all(
        table_name=TABLE_NAME, where={"twitch_user_id": twitch_user_id}, type_=BotConfigDB
    )


def insert_bot(twitch_user_id: str) -> Optional[int]:
    return PROGRAMM_PARTS.database.insert(table_name=TABLE_NAME, data={"twitch_user_id": twitch_user_id})


def update_bot(bot_id: int, data: dict[str, Any]) -> bool:
    return PROGRAMM_PARTS.database.update(table_name=TABLE_NAME, where={"id": bot_id}, data=data)


def delete_bot(bot_id: int) -> bool:
    return PROGRAMM_PARTS.database.delete(table_name=TABLE_NAME, where={"id": bot_id})
