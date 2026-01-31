from datetime import datetime
from datetime import timedelta
from typing import Final

import httpx

from bot.core.types.programm_parts import PROGRAMM_PARTS
from bot.database.discord_auth import select_discord_tokens
from bot.frontend.types.discord_guild import DiscordGuild
from bot.helpers.log import LogProgram
from bot.helpers.log import log_exception

DISCORD_SERVER_CACHE: Final[dict[int, tuple[list[DiscordGuild], datetime]]] = {}
DISCORD_CHANNEL_CACHE: Final[dict[int, tuple[list[dict[str, str | int]], datetime]]] = {}


async def get_allowed_discord_servers(user_id: int) -> list[DiscordGuild]:
    if user_id in DISCORD_SERVER_CACHE:
        guilds, timestamp = DISCORD_SERVER_CACHE[user_id]
        if datetime.now() - timestamp < timedelta(minutes=5):
            return guilds

    tokens = select_discord_tokens(user_id)
    if tokens.value is None:
        return []

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                "https://discord.com/api/users/@me/guilds",
                headers={"Authorization": f"Bearer {tokens.value.access_token}"},
            )
            response.raise_for_status()
            guilds: list[DiscordGuild] = response.json()

            # Filter for guilds where the user has Admin rights.
            # Administrator permission bit is 0x8 (1 << 3).
            # We also check if the user is the owner.
            allowed_guilds: list[DiscordGuild] = []
            for guild in guilds:
                permissions = int(guild["permissions"])
                is_admin = (permissions & 0x8) == 0x8
                if is_admin or guild["owner"]:
                    allowed_guilds.append(guild)

            DISCORD_SERVER_CACHE[user_id] = (allowed_guilds, datetime.now())
            return allowed_guilds
        except Exception as e:
            log_exception(e, LogProgram.Default, f"Failed to get allowed discord servers for user {user_id}")
            return []


def get_discord_channels(server_id: int) -> list[dict[str, str | int]]:
    if server_id in DISCORD_CHANNEL_CACHE:
        channels, timestamp = DISCORD_CHANNEL_CACHE[server_id]
        if datetime.now() - timestamp < timedelta(minutes=5):
            return channels

    discord_channels = []
    if PROGRAMM_PARTS.discord is not None:
        guild = PROGRAMM_PARTS.discord.get_guild(server_id)
        if guild is not None:
            discord_channels = [{"id": channel.id, "name": channel.name} for channel in guild.text_channels]
            DISCORD_CHANNEL_CACHE[server_id] = (discord_channels, datetime.now())

    return discord_channels
