import asyncio
from typing import Optional

from bot.chat.twitch_client import TwitchClient
from bot.core.types.programm_parts import PROGRAMM_PARTS
from bot.database.types.twitch_broadcast_message import TwitchBroadcastMessageDB
from bot.helpers.log import LogLevel
from bot.helpers.log import log_default


async def handle_broadcast_messages() -> None:
    twitch: Optional[TwitchClient] = PROGRAMM_PARTS.twitch
    if twitch is None:
        log_default(LogLevel.ERROR, "Twitch bot is not running. Skipping broadcast message handling...")
        return

    async def _send_messages(twitch_: TwitchClient, messages_: list[TwitchBroadcastMessageDB]) -> None:
        for message in messages_:
            for chat in twitch_.chats:
                if chat.bot_id == message.bot_id and chat.channel_name == message.channel_name:
                    await chat.send_broadcast_message(message.message)
                    continue

    while True:
        broadcast = PROGRAMM_PARTS.broadcast
        if broadcast is None:
            log_default(LogLevel.ERROR, "Broadcast handler is not running. Skipping broadcast message handling...")
            return

        messages = broadcast.get_next_messages()
        await _send_messages(twitch, messages)
        log_default(LogLevel.DEBUG, f"Sent {len(messages)} broadcast messages")
        await asyncio.sleep(60)
