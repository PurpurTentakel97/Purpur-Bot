from bot.chat.discord_client import DiscordClient
from bot.chat.discord_server import DiscordServer
from bot.chat.twitch_chat import TwitchChat
from bot.chat.twitch_client import TwitchClient
from bot.core.broadcast_messages import get_all_broadcast_messages as get_all_broadcast_messages_core
from bot.core.discord_feature_flags import (
    select_discord_feature_flags_by_server_id as select_discord_feature_flags_by_server_id_core,
)
from bot.core.twitch_feature_flags import (
    select_twitch_feature_flags_by_channel_name as select_twitch_feature_flags_by_channel_name_core,
)
from bot.core.types.broadcast_message_storrage import BroadcastMessageStorage
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

    if (
        servers.value is None
    ):  # should never happen since an empty list gets returned normally when no data is available
        log_default(LogLevel.ERROR, "Discord Servers not found. Aborting start Bots...")
        return

    for server in servers.value:
        feature_flags = select_discord_feature_flags_by_server_id_core(server.bot_id, server.server_id)
        if feature_flags.value is None:
            log_default(LogLevel.ERROR, f"Discord Feature Flags for server {server.server_id} not found. Skipping...")
            continue  # should never happen.
        discord_server = DiscordServer(server.bot_id, server.server_id)
        PROGRAMM_PARTS.discord.connect_server(discord_server)


async def _start_twitch_bot() -> None:
    PROGRAMM_PARTS.twitch = await TwitchClient.create()

    if PROGRAMM_PARTS.twitch is None:
        return

    channels = PROGRAMM_PARTS.database.select_all(table_name="bot_twitch_lookup", where={}, type_=TwitchChannelDB)

    if (
        channels.value is None
    ):  # should never happen since an empty list gets returned normally when no data is available
        log_default(LogLevel.ERROR, "Twitch Channels not found. Aborting start Bots...")
        return

    for channel in channels.value:
        feature_flags = select_twitch_feature_flags_by_channel_name_core(channel.bot_id, channel.channel_name)
        if feature_flags.value is None:
            log_default(
                LogLevel.ERROR, f"Twitch Feature Flags for channel {channel.channel_name} not found. Skipping..."
            )
            continue
        await TwitchChat.create(PROGRAMM_PARTS.twitch, channel.bot_id, channel.channel_name)


def _start_broadcast() -> None:
    broadcast_messages = get_all_broadcast_messages_core()
    if broadcast_messages.state.fail or broadcast_messages.value is None:
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
