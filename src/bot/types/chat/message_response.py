from typing import TYPE_CHECKING
from typing import Any
from typing import final

from attr import dataclass
from discord import Message as DiscordMessage
from twitchAPI.chat import ChatMessage as TwitchChatMessage

if TYPE_CHECKING:
    from bot.chat.twitch_chat import Chat


@final
@dataclass
class ChatMessageResponse:
    text: str
    destination_chat: "Chat"
    original_message: DiscordMessage | TwitchChatMessage
    meta_data: Any
