from bot.core.types.programm_parts import PROGRAMM_PARTS
from bot.core.types.result import Result
from bot.database.types.discord_auth import DiscordAuthDB

TABLE_NAME = "discord_auth"


def select_discord_tokens(discord_id: int) -> Result[DiscordAuthDB]:
    return PROGRAMM_PARTS.database.select_one(
        table_name=TABLE_NAME, where={"discord_id": discord_id}, type_=DiscordAuthDB
    )


def insert_discord_tokens(discord_id: int, access_token: str, refresh_token: str, expires_at: int) -> Result[int]:
    return PROGRAMM_PARTS.database.insert(
        TABLE_NAME,
        {
            "discord_id": discord_id,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expires_at": expires_at,
        },
    )


def update_discord_tokens(discord_id: int, access_token: str, refresh_token: str, expires_at: int) -> Result[None]:
    return PROGRAMM_PARTS.database.update(
        table_name=TABLE_NAME,
        data={"access_token": access_token, "refresh_token": refresh_token, "expires_at": expires_at},
        where={"discord_id": discord_id},
    )


def delete_discord_tokens(discord_id: int) -> Result[None]:
    return PROGRAMM_PARTS.database.delete(table_name=TABLE_NAME, where={"discord_id": discord_id})
