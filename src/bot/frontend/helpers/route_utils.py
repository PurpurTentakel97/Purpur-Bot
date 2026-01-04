from datetime import datetime
from functools import lru_cache
from pathlib import Path
from typing import Final

import jwt
from starlette.requests import Request
from starlette.templating import Jinja2Templates

from bot.frontend.helpers.auth_constents import JWT_ALG
from bot.helpers.app_context import APP_CONTEXT
from bot.helpers.log import LogProgram
from bot.helpers.log import log_exception
from bot.types.twitch_session_cookie_jwt import TwitchSessionCookie


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
