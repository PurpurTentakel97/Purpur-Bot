from bot.core.types.programm_parts import PROGRAMM_PARTS
from bot.core.types.result import Result
from bot.database.types.twitch_auth import TwitchAuthDB

TABLE_NAME = "twitch_auth"


def select_twitch_tokens(twitch_id: str) -> Result[TwitchAuthDB]:
    return PROGRAMM_PARTS.database.select_one(table_name=TABLE_NAME, where={"twitch_id": twitch_id}, type_=TwitchAuthDB)


def insert_twitch_tokens(twitch_id: str, access_token: str, refresh_token: str, expires_at: int) -> Result[int]:
    return PROGRAMM_PARTS.database.insert(
        TABLE_NAME,
        {
            "twitch_id": twitch_id,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expires_at": expires_at,
        },
    )


def update_twitch_tokens(twitch_id: str, access_token: str, refresh_token: str, expires_at: int) -> Result[None]:
    return PROGRAMM_PARTS.database.update(
        table_name=TABLE_NAME,
        data={"access_token": access_token, "refresh_token": refresh_token, "expires_at": expires_at},
        where={"twitch_id": twitch_id},
    )


def delete_twitch_tokens(twitch_id: str) -> Result[None]:
    return PROGRAMM_PARTS.database.delete(table_name=TABLE_NAME, where={"twitch_id": twitch_id})
