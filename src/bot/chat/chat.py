import asyncio

from bot.types.chat_message import ChatMessage
from bot.types.feature_flag import FeatureFlags


# todo: make abstract when it comes to sending messages
class Chat:
    def __init__(self, id_: int, features: FeatureFlags) -> None:
        self._id: int = id_
        self._feature_flags: FeatureFlags = features
        self.message_queue: asyncio.Queue[ChatMessage] = asyncio.Queue()

    @property
    def id(self) -> int:
        return self._id

    @property
    def feature_flags(self) -> FeatureFlags:
        return self._feature_flags

    async def get_next_message(self) -> ChatMessage | None:
        if self.message_queue.empty():
            return None
        return await self.message_queue.get()
