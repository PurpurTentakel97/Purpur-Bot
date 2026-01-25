from bot.core.types.programm_parts import PROGRAMM_PARTS
from bot.core.types.result import Result
from bot.database.types.fields import FIELD_ACCESS_TOKEN
from bot.database.types.fields import FIELD_EXPIRES_AT
from bot.database.types.fields import FIELD_REFRESH_TOKEN
from bot.database.types.fields import FIELD_TWITCH_USER_ID
from bot.database.types.fields import TABLE_TWITCH_AUTH_NAME
from bot.database.types.twitch_auth import TwitchAuthDB


def select_twitch_tokens(twitch_id: str) -> Result[TwitchAuthDB]:
    return PROGRAMM_PARTS.database.select_one(
        table_name=TABLE_TWITCH_AUTH_NAME, where={FIELD_TWITCH_USER_ID: twitch_id}, type_=TwitchAuthDB
    )


def insert_twitch_tokens(twitch_id: str, access_token: str, refresh_token: str, expires_at: int) -> Result[int]:
    return PROGRAMM_PARTS.database.insert(
        TABLE_TWITCH_AUTH_NAME,
        {
            FIELD_TWITCH_USER_ID: twitch_id,
            FIELD_ACCESS_TOKEN: access_token,
            FIELD_REFRESH_TOKEN: refresh_token,
            FIELD_EXPIRES_AT: expires_at,
        },
    )


def update_twitch_tokens(twitch_id: str, access_token: str, refresh_token: str, expires_at: int) -> Result[None]:
    return PROGRAMM_PARTS.database.update(
        table_name=TABLE_TWITCH_AUTH_NAME,
        data={FIELD_ACCESS_TOKEN: access_token, FIELD_REFRESH_TOKEN: refresh_token, FIELD_EXPIRES_AT: expires_at},
        where={FIELD_TWITCH_USER_ID: twitch_id},
    )


def delete_twitch_tokens(twitch_id: str) -> Result[None]:
    return PROGRAMM_PARTS.database.delete(table_name=TABLE_TWITCH_AUTH_NAME, where={FIELD_TWITCH_USER_ID: twitch_id})
