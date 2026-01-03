from http import HTTPStatus
from typing import Annotated
from typing import Final
from typing import Optional

import jwt
from fastapi import Depends
from fastapi import HTTPException
from starlette.requests import Request

from bot.frontend.helpers.auth_constents import JWT_ALG
from bot.helpers.app_context import APP_CONTEXT
from bot.types.twitch_user_info import TwitchUserInfo


def get_twitch_user(request: Request) -> Optional[TwitchUserInfo]:
    session_cookie = request.cookies.get("TWITCH_SESSION_COOKIE")
    if session_cookie is None:
        return None

    try:
        payload: Final = jwt.decode(  # type: ignore[reportUnknownMemberType]
            jwt=session_cookie,
            key=APP_CONTEXT.jwt_secret.value(),
            algorithms=JWT_ALG,
        )
        return TwitchUserInfo(
            id_=payload["sub"],
            login=payload["login"],
            display_name=payload["display_name"],
            profile_image_url=payload.get("profile_image_url", ""),
        )
    except (jwt.InvalidTokenError, KeyError):
        return None


def get_authenticated_user(
    current_user: Annotated[Optional[TwitchUserInfo], Depends(get_twitch_user)],
) -> TwitchUserInfo:
    if current_user is None:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="Not authenticated")

    return current_user
