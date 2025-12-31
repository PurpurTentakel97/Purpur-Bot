from typing import TYPE_CHECKING
from typing import Any
from typing import final

from attr import dataclass

if TYPE_CHECKING:
    from bot.chat.twitch_chat import Chat


@final
@dataclass
class ResponseMessage:
    text: str
    destination_chat: "Chat"
    meta_data: Any
