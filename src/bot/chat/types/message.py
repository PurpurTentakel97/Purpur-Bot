from typing import TYPE_CHECKING
from typing import Any
from typing import final

from attr import dataclass
from discord import Message as DiscordMessage
from twitchAPI.chat import ChatMessage as TwitchChatMessage

from bot.core.types.permission_level import PermissionLevel

if TYPE_CHECKING:
    from bot.chat.twitch_chat import Chat


@final
@dataclass
class ChatMessage:
    id_: int
    text: str
    sender_chat: "Chat"
    sender_permission_level: PermissionLevel
    original_message: DiscordMessage | TwitchChatMessage
    meta_data: Any
