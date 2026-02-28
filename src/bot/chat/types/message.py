from typing import TYPE_CHECKING
from typing import Any
from typing import final

from attr import dataclass
from discord import Message as DiscordMessage
from twitchAPI.chat import ChatMessage as TwitchChatMessage

from bot.chat.discord_server import DiscordServer
from bot.chat.twitch_chat import TwitchChat
from bot.chat.types.message_response import ChatMessageResponse
from bot.core.types.permission_level import PermissionLevel

if TYPE_CHECKING:
    from bot.chat.twitch_chat import Chat


@final
@dataclass
class ChatMessage:
    bot_id: int
    text: str
    sender_chat: "Chat"
    sender_permission_level: PermissionLevel
    original_message: DiscordMessage | TwitchChatMessage
    meta_data: Any

    def to_response_message(self, response: str) -> ChatMessageResponse:
        return ChatMessageResponse(response, self.sender_chat, self.original_message, self.meta_data)

    @property
    def has_twitch_message(self) -> bool:
        return isinstance(self.sender_chat, TwitchChat)

    @property
    def has_discord_message(self) -> bool:
        return isinstance(self.sender_chat, DiscordServer)
