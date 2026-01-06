from typing import Optional

from bot.database.types import DiscordAuth
from bot.database.types import TwitchAuth
from bot.helpers.app_context import TwitchTokens
from bot.types.core.programm_parts import PROGRAMM_PARTS

TABLE_NAME_TWITCH = "twitch_auth"
TABLE_NAME_DISCORD = "discord_auth"


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


# discord get
def get_discord_tokens(discord_id: str) -> Optional[TwitchTokens]:
    discord_tokens = PROGRAMM_PARTS.database.find_one(
        table_name=TABLE_NAME_DISCORD, where={"discord_id": discord_id}, type_=DiscordAuth
    )

    if discord_tokens is None:
        return None

    return TwitchTokens(discord_tokens.access_token, discord_tokens.refresh_token)


# discord store update
def save_or_update_discord_tokens(discord_id: str, access_token: str, refresh_token: str, expires_at: int) -> bool:
    get_result = PROGRAMM_PARTS.database.find_one(
        table_name=TABLE_NAME_DISCORD, where={"discord_id": discord_id}, type_=DiscordAuth
    )

    if get_result is None:
        return PROGRAMM_PARTS.database.save(
            TABLE_NAME_DISCORD,
            {
                "discord_id": discord_id,
                "access_token": access_token,
                "refresh_token": refresh_token,
                "expires_at": expires_at,
            },
        )

    return PROGRAMM_PARTS.database.update(
        table_name=TABLE_NAME_DISCORD,
        data={"access_token": access_token, "refresh_token": refresh_token, "expires_at": expires_at},
        where={"discord_id": discord_id},
    )


# discord delete
def delete_discord_tokens(discord_id: str) -> bool:
    return PROGRAMM_PARTS.database.delete(table_name=TABLE_NAME_DISCORD, where={"discord_id": discord_id})
