import asyncio
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Final

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from bot.core.message_handler import handle_messages
from bot.frontend.routes.api import router as dashboard_router
from bot.frontend.routes.auth import router as auth_router
from bot.frontend.routes.home import router as home_router
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
app.mount("/static", StaticFiles(directory="src/bot/frontend/static"), name="static")
app.include_router(home_router)
app.include_router(auth_router)
app.include_router(login_router)
app.include_router(dashboard_router)
