import asyncio

from bot.core.commands import handle_command
from bot.helpers.log import LogLevel
from bot.helpers.log import log_default
from bot.helpers.log import log_discord
from bot.helpers.log import log_twitch
from bot.types.chat_message import ChatMessage
from bot.types.programm_parts import PROGRAMM_PARTS
from bot.types.response_message import ResponseMessage

# !command add|edit|remove NAME MESSAGE
# !dict add|edit|remove NAME MESSAGE


def handle_single_message(message: ChatMessage) -> list[ResponseMessage]:
    response_messages: list[ResponseMessage] = []

    if message.text.strip().startswith("!"):
        response = handle_command(message)
        if response is not None:
            response_messages.append(response)

    return response_messages


async def handle_messages() -> None:
    async def send_responses(messages: list[ResponseMessage]) -> None:
        if not messages:
            return

        first_message = messages[0]
        await first_message.destination_chat.send_response(messages)

    log_default(LogLevel.INFO, "message handler started")
    while True:
        if PROGRAMM_PARTS.twitch is not None:
            while True:
                message = await PROGRAMM_PARTS.twitch.get_next_message()
                if message is None:
                    break
                log_twitch(
                    LogLevel.DEBUG,
                    f"{message.sender_chat.id} | {message.sender_permission_level.name} | {message.text}",
                )
                responses = handle_single_message(message)
                await send_responses(responses)

        if PROGRAMM_PARTS.discord is not None:
            while True:
                message = await PROGRAMM_PARTS.discord.get_next_message()
                if message is None:
                    break
                log_discord(
                    LogLevel.DEBUG,
                    f"{message.sender_chat.id} | {message.sender_permission_level.name} | {message.text}",
                )
                responses = handle_single_message(message)
                await send_responses(responses)

        await asyncio.sleep(0.1)
