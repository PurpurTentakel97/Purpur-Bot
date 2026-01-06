import asyncio
from abc import ABC
from abc import abstractmethod

from bot.types.chat_message import ChatMessage
from bot.types.response_message import ResponseMessage


class Chat(ABC):
    def __init__(self, id_: int) -> None:
        self._id: int = id_
        self.message_queue: asyncio.Queue[ChatMessage] = asyncio.Queue()

    @property
    def id(self) -> int:
        return self._id

    async def get_next_message(self) -> ChatMessage | None:
        if self.message_queue.empty():
            return None
        return await self.message_queue.get()

    @abstractmethod
    async def send_response(self, messages: list[ResponseMessage]) -> None:
        pass
