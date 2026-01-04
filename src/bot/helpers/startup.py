# from bot.chat.discord_client import DiscordClient
# from bot.chat.discord_server import DiscordServer
from bot.chat.twitch_chat import TwitchChat
from bot.chat.twitch_client import TwitchClient
from bot.database.database import Database
from bot.database.types import TwitchChannel
from bot.helpers.log import LogLevel
from bot.helpers.log import log_default

# from bot.types.feature_flag import DEFAULT_DISCORD_FEATURES
from bot.types.feature_flag import DEFAULT_TWITCH_FEATURES
from bot.types.programm_parts import PROGRAMM_PARTS


def _start_database() -> None:
    value = Database.create()
    if value is not None:
        PROGRAMM_PARTS.database = value


# async def _start_discord_bot() -> None:
#    PROGRAMM_PARTS.discord = await DiscordClient.create()
#
#    if PROGRAMM_PARTS.discord is None:
#        return
#
#    for user in PROGRAMM_PARTS.config.user:
#        for channel in user.discord:
#            discord_server = DiscordServer(user.id, channel, DEFAULT_DISCORD_FEATURES)
#            PROGRAMM_PARTS.discord.connect_chat(discord_server)


async def _start_twitch_bot() -> None:
    PROGRAMM_PARTS.twitch = await TwitchClient.create()

    if PROGRAMM_PARTS.twitch is None:
        return

    channels = PROGRAMM_PARTS.database.find_all(table_name="bot_twitch_lookup", where={}, type_=TwitchChannel)

    for channel in channels:
        await TwitchChat.create(PROGRAMM_PARTS.twitch, channel.id, channel.channel_name, DEFAULT_TWITCH_FEATURES)


async def startup_programm() -> None:
    _start_database()

    if PROGRAMM_PARTS.database_unwrapped() is None:
        log_default(LogLevel.ERROR, "Database not existing. Aborting start Bots...")
        return

    #    await _start_discord_bot()
    await _start_twitch_bot()
