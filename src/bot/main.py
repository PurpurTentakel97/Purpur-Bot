import asyncio
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Final

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import FileResponse
from starlette.responses import Response

from bot.chat.message_handler import handle_messages
from bot.core.handle_broadcast_message import handle_broadcast_messages
from bot.core.startup import startup_programm
from bot.core.terminate import terminate_programm
from bot.frontend.helpers.decorators import get_optional_owned_discord_user
from bot.frontend.helpers.decorators import get_optional_owned_twitch_user
from bot.frontend.helpers.route_utils import get_templates
from bot.frontend.routes.api_auth import router as auth_router
from bot.frontend.routes.api_icons import router as icon_router
from bot.frontend.routes.api_names import router as frontend_api_router
from bot.frontend.routes.dashboard_alias import router as dashboard_alias_router
from bot.frontend.routes.dashboard_commands import router as dashboard_commands_router
from bot.frontend.routes.dashboard_counter import router as dashboard_counter_router
from bot.frontend.routes.dashboard_discord import router as dashboard_discord_router
from bot.frontend.routes.dashboard_global import router as dashboard_main_router
from bot.frontend.routes.dashboard_quotes import router as dashboard_quotes_router
from bot.frontend.routes.dashboard_twitch import router as dashboard_twitch_router
from bot.frontend.routes.home import router as home_router
from bot.frontend.routes.views import router as view_router
from bot.helpers.log import LogProgram
from bot.helpers.log import log_exception


@asynccontextmanager
async def main(_: FastAPI) -> AsyncGenerator[None]:
    await startup_programm()

    tasks = [
        asyncio.create_task(handle_messages()),
        asyncio.create_task(handle_broadcast_messages()),
    ]

    try:
        yield

    finally:
        for task in tasks:
            task.cancel()
        try:
            await asyncio.gather(*tasks, return_exceptions=True)
        except asyncio.CancelledError:
            pass

        await terminate_programm()


app: Final = FastAPI(lifespan=main)
app.mount("/static", StaticFiles(directory="src/bot/frontend/static"), name="static")
app.include_router(auth_router)
app.include_router(home_router)
app.include_router(icon_router)
app.include_router(dashboard_main_router)
app.include_router(dashboard_twitch_router)
app.include_router(dashboard_discord_router)
app.include_router(dashboard_commands_router)
app.include_router(dashboard_alias_router)
app.include_router(dashboard_counter_router)
app.include_router(frontend_api_router)
app.include_router(dashboard_quotes_router)
app.include_router(view_router)


@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException) -> Response:
    # This catches 404, 403, 500, etc.
    template = get_templates()

    # robustly try to get the users for the header
    try:
        twitch_user = get_optional_owned_twitch_user(request)
        discord_user = get_optional_owned_discord_user(request)
    except Exception:
        twitch_user = None
        discord_user = None

    return template.TemplateResponse(
        request=request,
        name="error.html",
        context={
            "status_code": exc.status_code,
            "detail": exc.detail,
            "twitch_user": twitch_user,
            "discord_user": discord_user,
        },
        status_code=exc.status_code,
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception) -> Response:
    log_exception(exc, LogProgram.Frontend, "")
    template = get_templates()

    # robustly try to get the users for the header
    try:
        twitch_user = get_optional_owned_twitch_user(request)
        discord_user = get_optional_owned_discord_user(request)
    except Exception:
        twitch_user = None
        discord_user = None

    return template.TemplateResponse(
        request=request,
        name="error.html",
        context={
            "status_code": 500,
            "detail": "An unexpected server error occurred.",
            "twitch_user": twitch_user,
            "discord_user": discord_user,
        },
        status_code=500,
    )


@app.get("/favicon.ico")
async def favicon() -> FileResponse:
    return FileResponse("src/bot/frontend/static/favicon.png")
