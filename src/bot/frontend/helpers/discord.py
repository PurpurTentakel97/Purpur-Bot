import httpx

from bot.database.twitch_auth import select_discord_tokens
from bot.frontend.types.discord_guild import DiscordGuild
from bot.helpers.log import LogProgram
from bot.helpers.log import log_exception


async def get_allowed_discord_servers(user_id: str) -> list[DiscordGuild]:
    tokens = select_discord_tokens(user_id)
    if tokens is None:
        return []

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                "https://discord.com/api/users/@me/guilds", headers={"Authorization": f"Bearer {tokens.access_token}"}
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

            return allowed_guilds
        except Exception as e:
            log_exception(e, LogProgram.Default, f"Failed to get allowed discord servers for user {user_id}")
            return []
