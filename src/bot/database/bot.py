from typing import Optional

from bot.database.types import BotConfig
from bot.types.programm_parts import PROGRAMM_PARTS


# get
def get_bots_by_twitch_id(twitch_user_id: str) -> list[BotConfig]:
    return PROGRAMM_PARTS.database.find_all(
        table_name="bot_config", where={"twitch_user_id": twitch_user_id}, type_=BotConfig
    )


# insert
def create_new_bot(twitch_user_id: str) -> Optional[int]:
    return PROGRAMM_PARTS.database.save_with_returned_id(
        table_name="bot_config", data={"twitch_user_id": twitch_user_id}
    )
