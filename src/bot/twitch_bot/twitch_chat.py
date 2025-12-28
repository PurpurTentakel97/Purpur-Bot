from typing import Self

from twitchAPI.chat import Chat
from twitchAPI.chat import ChatEvent
from twitchAPI.chat import EventData

from bot.helpers.log import LogLevel
from bot.helpers.log import log_twitch
from bot.twitch_bot.twitch_client import TwitchClient


class TwitchChat:
    def __init__(self, chat: Chat) -> None:
        self.chat = chat

        self.chat.register_event(ChatEvent.READY, self.on_ready)
        self.chat.register_event(ChatEvent.MESSAGE, self.on_message)

    @classmethod
    async def create(cls, twitch: TwitchClient) -> Self:
        chat = await Chat(twitch.client)
        return cls(chat)

    async def on_ready(self, ready_event: EventData) -> None:
        channel_name: str = "codingPurpurTentakel"
        await ready_event.chat.join_room(channel_name)
        log_twitch(LogLevel.INFO, f"Twitch chat connected to {channel_name}")

    async def on_message(self, event: ChatEvent) -> None:
        log_twitch(LogLevel.DEBUG, f"Received message: {event.MESSAGE}")
