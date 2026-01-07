import asyncio
from abc import ABC
from abc import abstractmethod

from bot.chat.types.message import ChatMessage
from bot.chat.types.message_response import ChatMessageResponse


class Chat(ABC):
    def __init__(self, bot_id: int) -> None:
        self._bot_id: int = bot_id
        self.message_queue: asyncio.Queue[ChatMessage] = asyncio.Queue()

    @property
    def bot_id(self) -> int:
        return self._bot_id

    async def get_next_message(self) -> ChatMessage | None:
        if self.message_queue.empty():
            return None
        return await self.message_queue.get()

    @abstractmethod
    async def send_response(self, messages: list[ChatMessageResponse]) -> None:
        pass
