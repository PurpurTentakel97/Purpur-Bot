from bot.core.types.programm_parts import PROGRAMM_PARTS
from bot.core.types.result import Result
from bot.database.types.fields import FIELD_ACCESS_TOKEN
from bot.database.types.fields import FIELD_BOT_ID
from bot.database.types.fields import FIELD_EXPIRES_AT
from bot.database.types.fields import FIELD_REFRESH_TOKEN
from bot.database.types.fields import FIELD_TWITCH_CHANNEL_NAME
from bot.database.types.fields import FIELD_TWITCH_USER_ID
from bot.database.types.fields import TABLE_TWITCH_BROADCAST_AUTH_NAME
from bot.database.types.twitch_broadcast_auth import TwitchBroadcastAuthDB


def select_broadcast_tokens(bot_id: int, channel_name: str) -> Result[TwitchBroadcastAuthDB]:
    return PROGRAMM_PARTS.database.select_one(
        table_name=TABLE_TWITCH_BROADCAST_AUTH_NAME,
        where={FIELD_BOT_ID: bot_id, FIELD_TWITCH_CHANNEL_NAME: channel_name},
        type_=TwitchBroadcastAuthDB,
    )


def insert_broadcast_tokens(
    bot_id: int, channel_name: str, twitch_user_id: str, access_token: str, refresh_token: str, expires_at: int
) -> Result[int]:
    return PROGRAMM_PARTS.database.insert(
        TABLE_TWITCH_BROADCAST_AUTH_NAME,
        {
            FIELD_BOT_ID: bot_id,
            FIELD_TWITCH_CHANNEL_NAME: channel_name,
            FIELD_TWITCH_USER_ID: twitch_user_id,
            FIELD_ACCESS_TOKEN: access_token,
            FIELD_REFRESH_TOKEN: refresh_token,
            FIELD_EXPIRES_AT: expires_at,
        },
    )


def update_broadcast_tokens(
    bot_id: int, channel_name: str, twitch_user_id: str, access_token: str, refresh_token: str, expires_at: int
) -> Result[None]:
    return PROGRAMM_PARTS.database.update(
        table_name=TABLE_TWITCH_BROADCAST_AUTH_NAME,
        data={
            FIELD_TWITCH_USER_ID: twitch_user_id,
            FIELD_ACCESS_TOKEN: access_token,
            FIELD_REFRESH_TOKEN: refresh_token,
            FIELD_EXPIRES_AT: expires_at,
        },
        where={FIELD_BOT_ID: bot_id, FIELD_TWITCH_CHANNEL_NAME: channel_name},
    )


def delete_broadcast_tokens(bot_id: int, channel_name: str) -> Result[None]:
    return PROGRAMM_PARTS.database.delete(
        table_name=TABLE_TWITCH_BROADCAST_AUTH_NAME,
        where={FIELD_BOT_ID: bot_id, FIELD_TWITCH_CHANNEL_NAME: channel_name},
    )
