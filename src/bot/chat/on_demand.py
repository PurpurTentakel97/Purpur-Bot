from bot.chat.discord_server import DiscordServer
from bot.chat.twitch_chat import TwitchChat
from bot.core.discord_feature_flags import (
    select_discord_feature_flags_by_server_id as select_discord_feature_flags_by_server_id_core,
)
from bot.core.twitch_feature_flags import (
    select_twitch_feature_flags_by_channel_name as select_twitch_feature_flags_by_channel_name_core,
)
from bot.core.types.programm_parts import PROGRAMM_PARTS
from bot.database.bot import FIELD_ENABLED
from bot.database.bot import select_bot as select_bot_db
from bot.database.discord import select_discord_servers_by as select_discord_servers_by_db
from bot.database.twitch import FIELD_BOT_ID
from bot.database.twitch import select_twitch_channels_by as select_twitch_channels_by_db
from bot.helpers.log import LogLevel
from bot.helpers.log import log_default


def _start_single_discord_bot(bot_id: int, server_id: int) -> bool:
    if PROGRAMM_PARTS.discord is None:
        return False

    feature_flags = select_discord_feature_flags_by_server_id_core(bot_id, server_id)
    if feature_flags.value is None:
        log_default(LogLevel.ERROR, f"Discord Feature Flags for server {server_id} not found. Skipping...")
        return False

    discord_server = DiscordServer(bot_id, server_id)
    PROGRAMM_PARTS.discord.connect_server(discord_server)
    return True


def start_single_discord_bot(bot_id: int, server_id: int) -> bool:
    bot = select_bot_db(bot_id)
    if bot.value is None:
        log_default(LogLevel.ERROR, f"Bot {bot_id} not found. Skipping...")
        return False

    if not bot.value.enabled:
        log_default(LogLevel.WARNING, f"Bot {bot_id} for discord server id {server_id} is disabled. Skipping...")
        return True

    return _start_single_discord_bot(bot_id, server_id)


async def stop_single_discord_bot(id_: int, server_id: int) -> bool:
    if PROGRAMM_PARTS.discord is None:
        return False

    for server in PROGRAMM_PARTS.discord.servers:
        if server.bot_id == id_ and server.server_id == server_id:
            PROGRAMM_PARTS.discord.remove_server(server)
            await PROGRAMM_PARTS.discord.leave_guild(server_id)
            return True

    return True


def start_all_discord_bots_from_bot(bot_id: int) -> None:
    if PROGRAMM_PARTS.discord is None:
        return

    bot = select_bot_db(bot_id)
    if bot.value is None or bot.state.fail:
        log_default(LogLevel.ERROR, f"Bot {bot_id} not found. Skipping...")
        return

    if not bot.value.enabled:
        log_default(LogLevel.WARNING, f"Bot {bot_id} is disabled. Skipping...")
        return

    server = select_discord_servers_by_db({FIELD_BOT_ID: bot_id, FIELD_ENABLED: True})
    if server.state.fail or server.value is None:
        log_default(LogLevel.ERROR, f"Discord Servers for bot {bot_id} not found. Skipping...")
        return

    for s in server.value:
        _start_single_discord_bot(bot_id, s.server_id)


async def stop_all_discord_bots_from_bot(bot_id: int) -> None:
    if PROGRAMM_PARTS.discord is None:
        return

    for server in PROGRAMM_PARTS.discord.servers:
        if server.bot_id == bot_id:
            PROGRAMM_PARTS.discord.remove_server(server)
            await PROGRAMM_PARTS.discord.leave_guild(server.server_id)


async def _start_single_twitch_bot(bot_id: int, channel_name: str) -> bool:
    if PROGRAMM_PARTS.twitch is None:
        return False

    feature_flags = select_twitch_feature_flags_by_channel_name_core(bot_id, channel_name)
    if feature_flags.value is None:
        log_default(LogLevel.ERROR, f"Twitch Feature Flags for channel {channel_name} not found. Skipping...")
        return False

    await TwitchChat.create(PROGRAMM_PARTS.twitch, bot_id, channel_name)

    return True


async def start_single_twitch_bot(bot_id: int, channel_name: str) -> bool:
    if PROGRAMM_PARTS.twitch is None:
        return False

    bot = select_bot_db(bot_id)
    if bot.value is None:
        log_default(LogLevel.ERROR, f"Bot {bot_id} not found. Skipping...")
        return False

    if not bot.value.enabled:
        log_default(LogLevel.WARNING, f"Bot {bot_id} for twitch channel {channel_name} is disabled. Skipping...")
        return True

    return await _start_single_twitch_bot(bot_id, channel_name)


async def stop_single_twitch_bot(id_: int, channel_name: str) -> bool:
    if PROGRAMM_PARTS.twitch is None:
        return False

    for channel in PROGRAMM_PARTS.twitch.chats:
        if channel.bot_id == id_ and channel.channel_name == channel_name:
            await channel.terminate(PROGRAMM_PARTS.twitch)
            return True

    return True


async def start_all_twitch_bots_from_bot(bot_id: int) -> None:
    if PROGRAMM_PARTS.twitch is None:
        return

    bot = select_bot_db(bot_id)
    if bot.value is None or bot.state.fail:
        log_default(LogLevel.ERROR, f"Bot {bot_id} not found. Skipping...")
        return

    if not bot.value.enabled:
        log_default(LogLevel.WARNING, f"Bot {bot_id} is disabled. Skipping...")
        return

    channels = select_twitch_channels_by_db({FIELD_BOT_ID: bot_id, FIELD_ENABLED: True})
    if channels.state.fail or channels.value is None:
        log_default(LogLevel.ERROR, f"Twitch Channels for bot {bot_id} not found. Skipping...")
        return

    for channel in channels.value:
        await _start_single_twitch_bot(bot_id, channel.channel_name)


async def stop_all_twitch_bots_from_bot(bot_id: int) -> None:
    if PROGRAMM_PARTS.twitch is None:
        return

    for channel in PROGRAMM_PARTS.twitch.chats:
        if channel.bot_id == bot_id:
            await channel.terminate(PROGRAMM_PARTS.twitch)
