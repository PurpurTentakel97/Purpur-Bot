from typing import final
from typing import override

from discord import Member as DiscordMember
from discord.message import Message as DiscordMessage

from bot.chat.chat import Chat
from bot.chat.types.message import ChatMessage
from bot.chat.types.message_response import ChatMessageResponse
from bot.core.types.permission_level import PermissionLevel
from bot.helpers.log import LogLevel
from bot.helpers.log import log_discord


@final
class DiscordServer(Chat):
    def __init__(self, bot_id: int, server_id: int) -> None:
        super().__init__(bot_id)
        self._server_id: int = server_id

    @property
    def server_id(self) -> int:
        return self._server_id

    @property
    @override
    def is_discord(self) -> bool:
        return True

    @override
    async def send_response(self, messages: list[ChatMessageResponse]) -> None:
        for message in messages:
            if isinstance(message.original_message, DiscordMessage):
                await message.original_message.channel.send(message.text)
            else:
                log_discord(
                    LogLevel.ERROR,
                    "Could not reply to the provided original message due to type missmatch: "
                    + f"{type(message.original_message)}",
                )

    async def on_message(self, message: DiscordMessage) -> None:
        def _get_permission_level(user: DiscordMember) -> PermissionLevel:
            if user.guild_permissions.administrator:
                return PermissionLevel.ADMIN

            if user.guild_permissions.manage_messages:
                return PermissionLevel.MODERATOR

            if "vip" in user.roles or "VIP" in user.roles:
                return PermissionLevel.SPECIAL_USER

            return PermissionLevel.USER

        # the author is a member of the server by now since the client called this method.
        if not isinstance(message.author, DiscordMember):
            raise AssertionError("Expected author to be a Member")

        msg = ChatMessage(
            bot_id=self.bot_id,
            text=message.content,
            sender_chat=self,
            sender_permission_level=_get_permission_level(message.author),
            original_message=message,
            meta_data=None,
        )
        await self.message_queue.put(msg)
