import asyncio
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Final

from fastapi import FastAPI

from bot.core.message_handler import handle_messages
from bot.frontend.routes.login import router as login_router
from bot.helpers.startup import startup_programm
from bot.helpers.terminate import terminate_programm


@asynccontextmanager
async def main(_: FastAPI) -> AsyncGenerator[None]:
    await startup_programm()
    message_task = asyncio.create_task(handle_messages())

    try:
        yield

    finally:
        message_task.cancel()
        try:
            await message_task
        except asyncio.CancelledError:
            pass

        await terminate_programm()


app: Final = FastAPI(lifespan=main)
app.include_router(login_router)
