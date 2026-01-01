import asyncio

from bot.core.console import handle_console
from bot.core.message_handler import handle_messages
from bot.helpers.startup import startup_programm
from bot.helpers.terminate import terminate_programm


async def main() -> None:
    await startup_programm()
    message_task = asyncio.create_task(handle_messages())

    await asyncio.to_thread(handle_console)  # blocking

    message_task.cancel()
    try:
        await message_task
    except asyncio.CancelledError:
        pass

    await terminate_programm()


def start() -> None:
    asyncio.run(main())


if __name__ == "__main__":
    start()
