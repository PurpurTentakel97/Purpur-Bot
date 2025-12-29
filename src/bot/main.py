import asyncio

from bot.helpers.console import handle_console
from bot.helpers.startup import startup_programm
from bot.helpers.terminate import terminate_programm
from bot.types.programm_parts import ProgramParts


async def main() -> None:
    program: ProgramParts = await startup_programm()

    handle_console()  # blocking

    await terminate_programm(program)


def start() -> None:
    asyncio.run(main())


if __name__ == "__main__":
    start()
