from typing import Optional

from bot.types.programm_parts import PROGRAMM_PARTS


def create_new_bot(twitch_user_id: str) -> Optional[int]:
    return PROGRAMM_PARTS.database.save_with_returned_id(
        table_name="twitch_bot_mapping", data={"twitch_id": twitch_user_id}
    )
