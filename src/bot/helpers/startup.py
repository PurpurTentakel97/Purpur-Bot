from typing import Optional

from bot.discord_bot.discord_client import DiscordClient
from bot.discord_bot.discord_server import DiscordServer
from bot.twitch_bot.twitch_chat import TwitchChat
from bot.twitch_bot.twitch_client import TwitchClient
from bot.types.programm_parts import ProgramParts

DEBUG_ID = 1


async def _start_discord_bot() -> Optional[DiscordClient]:
    discord_client = await DiscordClient.create()

    if discord_client is None:
        return None

    discord_server = DiscordServer(DEBUG_ID, 1222634745448501330)
    discord_client.connect_chat(discord_server)
    return discord_client


async def _start_twitch_bot() -> Optional[TwitchClient]:
    twitch_client = await TwitchClient.create()

    if twitch_client is None:
        return None

    await TwitchChat.create(twitch_client, DEBUG_ID, "codingPurpurTentakel")
    return twitch_client


async def startup_programm() -> ProgramParts:
    discord = await _start_discord_bot()
    twitch = await _start_twitch_bot()
    return ProgramParts(discord, twitch)
