from typing import final
from typing import override

import discord

from bot.chat.chat import Chat
from bot.types.chat_message import ChatMessage
from bot.types.feature_flag import FeatureFlags
from bot.types.permission_level import PermissionLevel
from bot.types.response_message import ResponseMessage


@final
class DiscordServer(Chat):
    def __init__(self, id_: int, server_id: int, features: FeatureFlags) -> None:
        super().__init__(id_, features)
        self._server_id: int = server_id

    @property
    def id(self) -> int:
        return self._id

    @property
    def server_id(self) -> int:
        return self._server_id

    @override
    async def send_response(self, messages: list[ResponseMessage]) -> None:
        for message in messages:
            await message.original_message.channel.send(message.text)

    async def on_message(self, message: discord.Message) -> None:
        def _get_permission_level(user: discord.Member) -> PermissionLevel:
            if user.guild_permissions.administrator:
                return PermissionLevel.ADMIN

            if user.guild_permissions.manage_messages:
                return PermissionLevel.MODERATOR

            if "vip" in user.roles or "VIP" in user.roles:
                return PermissionLevel.SPECIAL_USER

            return PermissionLevel.USER

        # the author is a member of the server by now since the client called this method.
        if not isinstance(message.author, discord.Member):
            raise AssertionError("Expected author to be a Member")

        msg = ChatMessage(
            id_=self._id,
            text=message.content,
            sender_chat=self,
            sender_permission_level=_get_permission_level(message.author),
            original_message=message,
            meta_data=None,
        )
        await self.message_queue.put(msg)
