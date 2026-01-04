from http import HTTPStatus
from typing import Annotated
from typing import Optional

import jwt
from fastapi import Depends
from fastapi import HTTPException
from starlette.requests import Request

from bot.frontend.helpers.route_utils import get_twitch_session_cookie
from bot.types.twitch_user_info import TwitchUserInfo


def get_twitch_user(request: Request) -> Optional[TwitchUserInfo]:
    session_cookie = get_twitch_session_cookie(request)
    if session_cookie is None:
        return None

    try:
        return TwitchUserInfo(
            id_=session_cookie.user_id,
            login=session_cookie.login,
            display_name=session_cookie.display_name,
            profile_image_url=session_cookie.profile_image_url,
        )
    except (jwt.InvalidTokenError, KeyError):
        return None


def get_authenticated_twitch_user(
    current_user: Annotated[Optional[TwitchUserInfo], Depends(get_twitch_user)],
) -> TwitchUserInfo:
    if current_user is None:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="Not authenticated")

    return current_user
