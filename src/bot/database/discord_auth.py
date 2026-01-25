from bot.core.types.programm_parts import PROGRAMM_PARTS
from bot.core.types.result import Result
from bot.database.types.discord_auth import DiscordAuthDB
from bot.database.types.fields import FIELD_ACCESS_TOKEN
from bot.database.types.fields import FIELD_DISCORD_SERVER_ID
from bot.database.types.fields import FIELD_EXPIRES_AT
from bot.database.types.fields import FIELD_REFRESH_TOKEN
from bot.database.types.fields import TABLE_DISCORD_AUTH_NAME


def select_discord_tokens(discord_id: int) -> Result[DiscordAuthDB]:
    return PROGRAMM_PARTS.database.select_one(
        table_name=TABLE_DISCORD_AUTH_NAME, where={FIELD_DISCORD_SERVER_ID: discord_id}, type_=DiscordAuthDB
    )


def insert_discord_tokens(discord_id: int, access_token: str, refresh_token: str, expires_at: int) -> Result[int]:
    return PROGRAMM_PARTS.database.insert(
        TABLE_DISCORD_AUTH_NAME,
        {
            FIELD_DISCORD_SERVER_ID: discord_id,
            FIELD_ACCESS_TOKEN: access_token,
            FIELD_REFRESH_TOKEN: refresh_token,
            FIELD_EXPIRES_AT: expires_at,
        },
    )


def update_discord_tokens(discord_id: int, access_token: str, refresh_token: str, expires_at: int) -> Result[None]:
    return PROGRAMM_PARTS.database.update(
        table_name=TABLE_DISCORD_AUTH_NAME,
        data={FIELD_ACCESS_TOKEN: access_token, FIELD_REFRESH_TOKEN: refresh_token, FIELD_EXPIRES_AT: expires_at},
        where={FIELD_DISCORD_SERVER_ID: discord_id},
    )


def delete_discord_tokens(discord_id: int) -> Result[None]:
    return PROGRAMM_PARTS.database.delete(
        table_name=TABLE_DISCORD_AUTH_NAME, where={FIELD_DISCORD_SERVER_ID: discord_id}
    )
