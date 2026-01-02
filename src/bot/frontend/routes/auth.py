from typing import Final
from urllib.parse import urlencode

from fastapi import APIRouter
from starlette.requests import Request
from starlette.responses import RedirectResponse

from bot.frontend.helpers.auth_constents import TWITCH_SCOPES
from bot.helpers.app_context import APP_CONTEXT

router: Final = APIRouter()


@router.get("/login/twitch")
async def login_twitch() -> RedirectResponse:
    client_id = APP_CONTEXT.twitch_client_id.value_or_rise()
    redirect_uri = APP_CONTEXT.twitch_redirect_uri.value()

    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": " ".join([s.value for s in TWITCH_SCOPES]),
    }
    url = f"https://id.twitch.tv/oauth2/authorize?{urlencode(params)}"
    return RedirectResponse(url)


@router.get("/login/twitch/callback")
async def login_twitch_callback(request: Request) -> RedirectResponse:
    return RedirectResponse(url="/")


@router.get("login/discord")
async def login_discord() -> RedirectResponse:
    return RedirectResponse(url="/")


@router.get("login/discord/callback")
async def login_discord_callback(request: Request) -> RedirectResponse:
    return RedirectResponse(url="/")


@router.get("/logout")
async def logout() -> RedirectResponse:
    return RedirectResponse(url="/")
