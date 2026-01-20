import asyncio
from typing import cast

from bot.chat.alias_dict import lookup_aliases
from bot.chat.chat import Chat
from bot.chat.discord_server import DiscordServer
from bot.chat.handle_commands import handle_command
from bot.chat.twitch_chat import TwitchChat
from bot.chat.types.message import ChatMessage
from bot.chat.types.message_response import ChatMessageResponse
from bot.core.discord_feature_flags import (
    select_discord_feature_flags_by_server_id as select_discord_feature_flags_by_server_id_core,
)
from bot.core.twitch_feature_flags import (
    select_twitch_feature_flags_by_channel_name as select_twitch_feature_flags_by_channel_name_core,
)
from bot.core.types.programm_parts import PROGRAMM_PARTS
from bot.core.types.result import Result
from bot.core.types.result import ResultState
from bot.database.types.feature_flags import FeatureFlagsDB
from bot.helpers.log import LogLevel
from bot.helpers.log import log_default
from bot.helpers.log import log_discord
from bot.helpers.log import log_twitch


def _get_feature_flags(chat: Chat) -> Result[FeatureFlagsDB]:
    if chat.is_twitch:
        twitch_chat = cast(TwitchChat, chat)
        result = select_twitch_feature_flags_by_channel_name_core(twitch_chat.bot_id, twitch_chat.channel_name)
        if result.state.fail or result.value is None:
            return Result(ResultState.ERROR, None)
        return result.cast_to(FeatureFlagsDB, result.value)

    if chat.is_discord:
        discord_chat = cast(DiscordServer, chat)
        result = select_discord_feature_flags_by_server_id_core(discord_chat.bot_id, discord_chat.server_id)
        if result.state.fail or result.value is None:
            return Result(ResultState.ERROR, None)
        return result.cast_to(FeatureFlagsDB, result.value)

    return Result(ResultState.ERROR, None)


def handle_single_message(message: ChatMessage) -> list[ChatMessageResponse]:
    feature_flags = _get_feature_flags(message.sender_chat)
    if feature_flags.value is None:
        log_default(LogLevel.ERROR, f"failed to get feature flags for chat {message.sender_chat}")
        return []

    response_messages: list[ChatMessageResponse] = []

    if feature_flags.value.can_alias:
        alias_response = lookup_aliases(message)
        response_messages.extend(alias_response)

    if message.text.strip().startswith("!"):
        command_response = handle_command(message, feature_flags.value)
        if command_response is not None:
            response_messages.append(command_response)

    return list(reversed(response_messages))


async def handle_messages() -> None:
    async def send_responses(messages: list[ChatMessageResponse]) -> None:
        if not messages:
            return

        first_message = messages[0]
        await first_message.destination_chat.send_response(messages)

    log_default(LogLevel.INFO, "message handler started")
    while True:
        if PROGRAMM_PARTS.twitch is not None:
            while True:
                message = await PROGRAMM_PARTS.twitch.get_next_message()
                if message is None:
                    break
                log_twitch(
                    LogLevel.DEBUG,
                    f"{message.sender_chat.bot_id} | {message.sender_permission_level.name} | {message.text}",
                )
                responses = handle_single_message(message)
                await send_responses(responses)

        if PROGRAMM_PARTS.discord is not None:
            while True:
                message = await PROGRAMM_PARTS.discord.get_next_message()
                if message is None:
                    break
                log_discord(
                    LogLevel.DEBUG,
                    f"{message.sender_chat.bot_id} | {message.sender_permission_level.name} | {message.text}",
                )
                responses = handle_single_message(message)
                await send_responses(responses)

        await asyncio.sleep(0.1)
