from bot.chat.discord_client import DiscordClient
from bot.chat.discord_server import DiscordServer
from bot.chat.twitch_chat import TwitchChat
from bot.chat.twitch_client import TwitchClient
from bot.core.types.programm_parts import PROGRAMM_PARTS
from bot.database.database import Database
from bot.database.types.discord_server import DiscordServerDB
from bot.database.types.twitch_channel import TwitchChannelDB
from bot.helpers.log import LogLevel
from bot.helpers.log import log_default


def _start_database() -> None:
    value = Database.create()
    if value is not None:
        PROGRAMM_PARTS.database = value


async def _start_discord_bot() -> None:
    PROGRAMM_PARTS.discord = await DiscordClient.create()

    if PROGRAMM_PARTS.discord is None:
        return

    servers = PROGRAMM_PARTS.database.select_all(table_name="bot_discord_lookup", where={}, type_=DiscordServerDB)

    for server in servers:
        discord_server = DiscordServer(server.bot_id, server.server_id)
        PROGRAMM_PARTS.discord.connect_server(discord_server)


async def _start_twitch_bot() -> None:
    PROGRAMM_PARTS.twitch = await TwitchClient.create()

    if PROGRAMM_PARTS.twitch is None:
        return

    channels = PROGRAMM_PARTS.database.select_all(table_name="bot_twitch_lookup", where={}, type_=TwitchChannelDB)

    for channel in channels:
        await TwitchChat.create(PROGRAMM_PARTS.twitch, channel.bot_id, channel.channel_name)


async def startup_programm() -> None:
    _start_database()

    if PROGRAMM_PARTS.database_unwrapped() is None:
        log_default(LogLevel.ERROR, "Database not existing. Aborting start Bots...")
        return

    await _start_discord_bot()
    await _start_twitch_bot()
