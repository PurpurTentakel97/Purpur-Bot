from bot.chat.types.message import ChatMessage
from bot.chat.types.message_response import ChatMessageResponse
from bot.core.alias_dict import alias_lookup as alias_lookup_core


def lookup_aliases(message: ChatMessage) -> list[ChatMessageResponse]:
    messages = alias_lookup_core(message.bot_id, message.text)

    if messages.state.fail or messages.value is None or len(messages.value) == 0:
        return []

    return [message.to_response_message(entry) for entry in messages.value]
