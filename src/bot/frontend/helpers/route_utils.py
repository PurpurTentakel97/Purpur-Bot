from datetime import datetime
from functools import lru_cache
from http import HTTPStatus
from pathlib import Path
from typing import Final

import jwt
from fastapi import HTTPException
from starlette.requests import Request
from starlette.templating import Jinja2Templates

from bot.core.app_context import APP_CONTEXT
from bot.core.bot import get_bot as get_bot_core
from bot.database.types.bot_config import BotConfigDB
from bot.frontend.helpers.auth_constents import JWT_ALG
from bot.frontend.types.discord_session_cookie_jwt import DiscordSessionCookie
from bot.frontend.types.twitch_session_cookie_jwt import TwitchSessionCookie
from bot.helpers.log import LogProgram
from bot.helpers.log import log_exception


@lru_cache
def get_templates() -> Jinja2Templates:
    path = Path(__file__).parent.parent / "templates"

    if not path.exists():
        raise FileNotFoundError(f"Templates directory not found: {path}")

    templates = Jinja2Templates(directory=path)
    templates.env.globals["now"] = datetime.now()  # pyright: ignore [reportUnknownMemberType]
    return templates


def get_twitch_session_cookie(request: Request) -> TwitchSessionCookie | None:
    session_cookie = request.cookies.get("TWITCH_SESSION_COOKIE")
    if session_cookie is None:
        return None

    payload: Final = jwt.decode(  # pyright: ignore [reportUnknownMemberType]
        jwt=session_cookie,
        key=APP_CONTEXT.jwt_secret.value(),
        algorithms=JWT_ALG,
    )

    try:
        return TwitchSessionCookie.model_validate(payload)

    except Exception as e:
        log_exception(e, LogProgram.Default, "Failed to decode Twitch Session Cookie")
        return None


def get_discord_session_cookie(request: Request) -> DiscordSessionCookie | None:
    session_cookie = request.cookies.get("DISCORD_SESSION_COOKIE")
    if session_cookie is None:
        return None

    payload: Final = jwt.decode(  # pyright: ignore [reportUnknownMemberType]
        jwt=session_cookie,
        key=APP_CONTEXT.jwt_secret.value(),
        algorithms=JWT_ALG,
    )

    try:
        return DiscordSessionCookie.model_validate(payload)

    except Exception as e:
        log_exception(e, LogProgram.Default, "Failed to decode Discord Session Cookie")
        return None


def get_valid_bot(bot_id: int) -> BotConfigDB:
    result = get_bot_core(bot_id)

    if result.value is None:
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail="Bot not found")

    return result.value
