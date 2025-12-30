from typing import Optional

from bot.chat.discord_client import DiscordClient
from bot.chat.discord_server import DiscordServer
from bot.chat.twitch_chat import TwitchChat
from bot.chat.twitch_client import TwitchClient
from bot.helpers.config import ProgrammConfig
from bot.helpers.config import get_config
from bot.helpers.log import LogLevel
from bot.helpers.log import log_default
from bot.types.feature_flag import DEFAULT_DISCORD_FEATURES
from bot.types.feature_flag import DEFAULT_TWITCH_FEATURES
from bot.types.programm_parts import ProgramParts


async def _start_discord_bot(config: ProgrammConfig) -> Optional[DiscordClient]:
    discord_client = await DiscordClient.create()

    if discord_client is None:
        return None

    for user in config.user:
        for channel in user.discord:
            discord_server = DiscordServer(user.id, channel, DEFAULT_DISCORD_FEATURES)
            discord_client.connect_chat(discord_server)

    return discord_client


async def _start_twitch_bot(config: ProgrammConfig) -> Optional[TwitchClient]:
    twitch_client = await TwitchClient.create()

    if twitch_client is None:
        return None

    for user in config.user:
        for channel in user.twitch:
            await TwitchChat.create(twitch_client, user.id, channel, DEFAULT_TWITCH_FEATURES)

    return twitch_client


async def startup_programm() -> ProgramParts:
    config = get_config()
    if config is None:
        log_default(LogLevel.ERROR, "Config not existing. Aborting start Bots...")
        return ProgramParts(None, None, None)

    discord = await _start_discord_bot(config)
    twitch = await _start_twitch_bot(config)
    return ProgramParts(discord, twitch, config)
