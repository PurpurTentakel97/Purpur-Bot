from typing import Optional

from bot.database.types import TwitchAuth
from bot.helpers.app_context import TwitchTokens
from bot.types.programm_parts import PROGRAMM_PARTS

TABLE_NAME_TWITCH = "twitch_auth"


# get
def get_twitch_tokens(twitch_id: str) -> Optional[TwitchTokens]:
    twitch_tokens = PROGRAMM_PARTS.database.find_one(
        table_name=TABLE_NAME_TWITCH, where={"twitch_id": twitch_id}, type_=TwitchAuth
    )

    if twitch_tokens is None:
        return None

    return TwitchTokens(twitch_tokens.access_token, twitch_tokens.refresh_token)


# store update
def save_or_update_twitch_tokens(twitch_id: str, access_token: str, refresh_token: str, expires_at: int) -> bool:
    get_result = PROGRAMM_PARTS.database.find_one(
        table_name=TABLE_NAME_TWITCH, where={"twitch_id": twitch_id}, type_=TwitchAuth
    )

    if get_result is None:
        return PROGRAMM_PARTS.database.save(
            TABLE_NAME_TWITCH,
            {
                "twitch_id": twitch_id,
                "access_token": access_token,
                "refresh_token": refresh_token,
                "expires_at": expires_at,
            },
        )

    return PROGRAMM_PARTS.database.update(
        table_name=TABLE_NAME_TWITCH,
        data={"access_token": access_token, "refresh_token": refresh_token, "expires_at": expires_at},
        where={"twitch_id": twitch_id},
    )


# delete
def delete_twitch_tokens(twitch_id: str) -> bool:
    return PROGRAMM_PARTS.database.delete(table_name=TABLE_NAME_TWITCH, where={"twitch_id": twitch_id})
