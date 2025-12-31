import asyncio

from bot.core.commands import handle_command
from bot.helpers.log import LogLevel
from bot.helpers.log import log_default
from bot.helpers.log import log_discord
from bot.helpers.log import log_twitch
from bot.types.chat_message import ChatMessage
from bot.types.programm_parts import ProgramParts

# !command add|edit|remove NAME MESSAGE
# !dict add|edit|remove NAME MESSAGE


def handle_single_message(message: ChatMessage) -> None:
    if message.text.strip().startswith("!"):
        handle_command(message)


async def handle_messages(program: ProgramParts) -> None:
    log_default(LogLevel.INFO, "message handler started")
    while True:
        if program.twitch is not None:
            while True:
                message = await program.twitch.get_next_message()
                if message is None:
                    break
                log_twitch(
                    LogLevel.DEBUG,
                    f"{message.sender_chat.id} | {message.sender_permission_level.name} | {message.text}",
                )
                handle_single_message(message)

        if program.discord is not None:
            while True:
                message = await program.discord.get_next_message()
                if message is None:
                    break
                log_discord(
                    LogLevel.DEBUG,
                    f"{message.sender_chat.id} | {message.sender_permission_level.name} | {message.text}",
                )
                handle_single_message(message)

        await asyncio.sleep(0.1)
