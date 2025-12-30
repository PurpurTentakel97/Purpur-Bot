import asyncio

from bot.helpers.log import LogLevel
from bot.helpers.log import log_default
from bot.helpers.log import log_discord
from bot.helpers.log import log_twitch
from bot.types.programm_parts import ProgramParts


async def handle_messages(program: ProgramParts) -> None:
    log_default(LogLevel.INFO, "message handler started")
    while True:
        if program.twitch is not None:
            while True:
                message = await program.twitch.get_next_message()
                if message is None:
                    break
                log_twitch(
                    LogLevel.DEBUG, f"{message.sender_chat.id} | {message.sender_permission_level} | {message.text}"
                )

        if program.discord is not None:
            while True:
                message = await program.discord.get_next_message()
                if message is None:
                    break
                log_discord(
                    LogLevel.DEBUG, f"{message.sender_chat.id} | {message.sender_permission_level} | {message.text}"
                )

        await asyncio.sleep(0.1)
