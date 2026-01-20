from typing import Self
from typing import cast
from typing import final
from typing import override

from twitchAPI.chat import Chat as TwitchChatClient
from twitchAPI.chat import ChatEvent
from twitchAPI.chat import ChatMessage as TwitchChatMessage
from twitchAPI.chat import ChatUser
from twitchAPI.chat import EventData

from bot.chat.chat import Chat
from bot.chat.twitch_client import TwitchClient
from bot.chat.types.message import ChatMessage
from bot.chat.types.message_response import ChatMessageResponse
from bot.core.types.permission_level import PermissionLevel
from bot.helpers.log import LogLevel
from bot.helpers.log import log_twitch


@final
class TwitchChat(Chat):
    def __init__(self, chat: TwitchChatClient, bot_id: int, channel_name: str) -> None:
        super().__init__(bot_id)
        self.chat: TwitchChatClient = chat
        self._channel_name: str = channel_name

        async def _on_ready(ready_event: EventData) -> None:
            await self._on_ready(ready_event)

        async def _on_message(message: TwitchChatMessage) -> None:
            await self._on_message(message)

        self.chat.register_event(ChatEvent.READY, _on_ready)
        self.chat.register_event(ChatEvent.MESSAGE, _on_message)

        self.chat.start()

    @property
    def channel_name(self) -> str:
        return self._channel_name

    @classmethod
    async def create(
        cls,
        twitch: TwitchClient,
        id_: int,
        channel_name: str,
    ) -> Self:
        chat = await TwitchChatClient(twitch.client)
        instance = cls(chat, id_, channel_name)
        twitch.connect_chat(instance)
        return instance

    async def terminate(self, twitch: TwitchClient) -> None:
        self.chat.stop()
        twitch.disconnect_chat(self)
        log_twitch(LogLevel.INFO, f"Twitch chat for {self.channel_name} terminated.")

    @override
    async def send_response(self, messages: list[ChatMessageResponse]) -> None:
        for message in messages:
            await self.chat.send_message(self.channel_name, message.text)

    async def _on_ready(self, ready_event: EventData) -> None:
        await ready_event.chat.join_room(self.channel_name)
        log_twitch(LogLevel.INFO, f"Twitch chat connected to {self.channel_name}")

    async def _on_message(self, message: TwitchChatMessage) -> None:
        def _get_user_permission_level(user: ChatUser) -> PermissionLevel:
            # cast is needed because the lib does not provide a proper type hint for the result
            # however, the documentation ensures that badges are a dict or None
            badges = cast(dict[str, str] | None, user.badges)  # type: ignore[reportUnknownMemberType]
            if badges and "broadcaster" in badges:
                return PermissionLevel.ADMIN

            if user.mod:
                return PermissionLevel.MODERATOR

            if user.vip:
                return PermissionLevel.SPECIAL_USER

            return PermissionLevel.USER

        msg = ChatMessage(
            bot_id=self.bot_id,
            text=message.text,
            sender_chat=self,
            sender_permission_level=_get_user_permission_level(message.user),
            original_message=message,
            meta_data=None,
        )

        await self.message_queue.put(msg)
