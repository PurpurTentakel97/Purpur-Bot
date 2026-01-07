from typing import Optional

from bot.core.types.programm_parts import PROGRAMM_PARTS
from bot.database.types.bot_config import BotConfigDB

TABLE_NAME = "bot_config"


# bot
def select_bot(bot_id: int) -> Optional[BotConfigDB]:
    return PROGRAMM_PARTS.database.select_one(table_name=TABLE_NAME, where={"id": bot_id}, type_=BotConfigDB)


def select_bots_by_twitch_id(twitch_user_id: str) -> list[BotConfigDB]:
    return PROGRAMM_PARTS.database.select_all(
        table_name=TABLE_NAME, where={"twitch_user_id": twitch_user_id}, type_=BotConfigDB
    )


def insert_bot(twitch_user_id: str) -> Optional[int]:
    return PROGRAMM_PARTS.database.insert(table_name=TABLE_NAME, data={"twitch_user_id": twitch_user_id})


def update_bot(bot_id: int, twitch_id: str, new_name: str) -> bool:
    return PROGRAMM_PARTS.database.update(
        table_name=TABLE_NAME, where={"id": bot_id, "twitch_user_id": twitch_id}, data={"name": new_name}
    )


async def delete_bot(id_: int, twitch_user_id: str) -> bool:
    return PROGRAMM_PARTS.database.delete(table_name=TABLE_NAME, where={"id": id_, "twitch_user_id": twitch_user_id})
