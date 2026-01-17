import asyncio
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Final

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from bot.chat.message_handler import handle_messages
from bot.core.startup import startup_programm
from bot.core.terminate import terminate_programm
from bot.frontend.routes.api_auth import router as auth_router
from bot.frontend.routes.api_bot import router as api_bot_router
from bot.frontend.routes.api_icons import router as icon_router
from bot.frontend.routes.home import router as home_router


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
app.mount("/static", StaticFiles(directory="src/bot/frontend/static"), name="static")
app.include_router(api_bot_router)
app.include_router(auth_router)
app.include_router(home_router)
app.include_router(icon_router)
