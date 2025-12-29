from typing import Self

from twitchAPI.chat import Chat
from twitchAPI.chat import ChatEvent
from twitchAPI.chat import ChatMessage
from twitchAPI.chat import EventData

from bot.helpers.log import LogLevel
from bot.helpers.log import log_twitch
from bot.twitch_bot.twitch_client import TwitchClient


class TwitchChat:
    def __init__(self, chat: Chat, id_: int, channel_name: str) -> None:
        self.chat: Chat = chat
        self._id: int = id_
        self._channel_name: str = channel_name

        async def _on_ready(ready_event: EventData) -> None:
            await self._on_ready(ready_event)

        async def _on_message(message: ChatMessage) -> None:
            await self._on_message(message)

        self.chat.register_event(ChatEvent.READY, _on_ready)
        self.chat.register_event(ChatEvent.MESSAGE, _on_message)

        self.chat.start()

    @property
    def id(self) -> int:
        return self._id

    @property
    def channel_name(self) -> str:
        return self._channel_name

    @classmethod
    async def create(cls, twitch: TwitchClient, id_: int, channel_name: str) -> Self:
        chat = await Chat(twitch.client)
        return cls(chat, id_, channel_name)

    async def handle_command(self, command: str) -> None:
        log_twitch(LogLevel.DEBUG, f"Received command: {command}")
        await self.chat.send_message(self.channel_name, "!ping")

    async def _on_ready(self, ready_event: EventData) -> None:
        await ready_event.chat.join_room(self.channel_name)
        log_twitch(LogLevel.INFO, f"Twitch chat connected to {self.channel_name}")

    async def _on_message(self, message: ChatMessage) -> None:
        log_twitch(LogLevel.DEBUG, f"{self.channel_name} | {message.user.name}: {message.text}")
        if message.text.startswith("!"):
            await self.handle_command(message.text)
