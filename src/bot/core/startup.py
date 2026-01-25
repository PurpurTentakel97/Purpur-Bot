from bot.chat.discord_client import DiscordClient
from bot.chat.on_demand import start_single_discord_bot
from bot.chat.on_demand import start_single_twitch_bot
from bot.chat.twitch_client import TwitchClient
from bot.core.broadcast_messages import get_all_broadcast_messages as get_all_broadcast_messages_core
from bot.core.types.broadcast_message_storrage import BroadcastMessageStorage
from bot.core.types.programm_parts import PROGRAMM_PARTS
from bot.database.bot import FIELD_ENABLED
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

    servers = PROGRAMM_PARTS.database.select_all(
        table_name="bot_discord_lookup", where={FIELD_ENABLED: True}, type_=DiscordServerDB
    )

    if (
        servers.value is None
    ):  # should never happen since an empty list gets returned normally when no data is available
        log_default(LogLevel.ERROR, "Discord Servers not found. Aborting start Bots...")
        return

    for server in servers.value:
        if not server.enabled:
            log_default(
                LogLevel.WARNING, f"Discord Server {server.server_id} for Bot {server.bot_id} is disabled. Skipping..."
            )
            continue

        start_single_discord_bot(server.bot_id, server.server_id)


async def _start_twitch_bot() -> None:
    PROGRAMM_PARTS.twitch = await TwitchClient.create()

    if PROGRAMM_PARTS.twitch is None:
        return

    channels = PROGRAMM_PARTS.database.select_all(
        table_name="bot_twitch_lookup", where={FIELD_ENABLED: True}, type_=TwitchChannelDB
    )

    if (
        channels.value is None
    ):  # should never happen since an empty list gets returned normally when no data is available
        log_default(LogLevel.ERROR, "Twitch Channels not found. Aborting start Bots...")
        return

    for channel in channels.value:
        if not channel.enabled:
            log_default(
                LogLevel.WARNING,
                f"Twitch Channel {channel.channel_name}  for Bot {channel.bot_id} is disabled. Skipping...",
            )
            continue

        await start_single_twitch_bot(channel.bot_id, channel.channel_name)


def _start_broadcast() -> None:
    broadcast_messages = get_all_broadcast_messages_core()
    if broadcast_messages.value is None:
        log_default(LogLevel.ERROR, "Could not load broadcast messages. Aborting start Bots...")
        return
    PROGRAMM_PARTS.broadcast = BroadcastMessageStorage(broadcast_messages.value)


async def startup_programm() -> None:
    _start_database()

    if PROGRAMM_PARTS.database_unwrapped() is None:
        log_default(LogLevel.ERROR, "Database not existing. Aborting start Bots...")
        return

    await _start_discord_bot()
    await _start_twitch_bot()
    _start_broadcast()
