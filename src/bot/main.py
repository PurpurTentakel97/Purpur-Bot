import asyncio

from bot.helpers.console import handle_console
from bot.helpers.startup import startup_programm
from bot.helpers.terminate import terminate_programm
from bot.types.programm_parts import ProgramParts


async def main() -> None:
    program: ProgramParts = await startup_programm()

    await asyncio.to_thread(handle_console)

    await terminate_programm(program)


def start() -> None:
    asyncio.run(main())


if __name__ == "__main__":
    start()
