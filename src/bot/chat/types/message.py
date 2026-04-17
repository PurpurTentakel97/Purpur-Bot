from typing import TYPE_CHECKING
from typing import Any
from typing import Optional
from typing import final

from attr import dataclass
from discord import Message as DiscordMessage
from twitchAPI.chat import ChatMessage as TwitchChatMessage

from bot.chat.types.message_response import ChatMessageResponse
from bot.chat.types.user_ref import UserRef
from bot.core.types.permission_level import PermissionLevel

if TYPE_CHECKING:
    from bot.chat.twitch_chat import Chat


@final
@dataclass
class ChatMessage:
    bot_id: int
    text: str
    sender: UserRef
    mentions: list[UserRef]
    owner: UserRef
    sender_chat: "Chat"
    sender_permission_level: PermissionLevel
    original_message: DiscordMessage | TwitchChatMessage
    meta_data: Any

    def to_response_message(self, response: str) -> ChatMessageResponse:
        return ChatMessageResponse(response, self.sender_chat, self.original_message, self.meta_data)

    @property
    def has_twitch_message(self) -> bool:
        return self.sender_chat.is_twitch

    @property
    def has_discord_message(self) -> bool:
        return self.sender_chat.is_discord

    def try_get_twitch_broadcaster_id(self) -> Optional[str]:
        if not isinstance(self.original_message, TwitchChatMessage):
            return None

        if self.original_message.room is None:
            return None

        return self.original_message.room.room_id

    def try_get_discord_server_id(self) -> Optional[int]:
        if not isinstance(self.original_message, DiscordMessage):
            return None

        if self.original_message.guild is None:
            return None

        return self.original_message.guild.id

    def try_get_discord_channel_id(self) -> Optional[int]:
        if not isinstance(self.original_message, DiscordMessage):
            return None

        return self.original_message.channel.id
