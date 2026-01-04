import secrets
from datetime import UTC
from datetime import datetime
from datetime import timedelta
from http import HTTPStatus
from typing import Annotated
from typing import Final
from typing import Optional
from typing import cast
from urllib.parse import urlencode

import jwt
from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from starlette.requests import Request
from starlette.responses import RedirectResponse
from twitchAPI.helper import first
from twitchAPI.oauth import UserAuthenticator
from twitchAPI.oauth import revoke_token
from twitchAPI.twitch import Twitch

from bot.database.auth import delete_twitch_tokens
from bot.database.auth import get_twitch_tokens
from bot.database.auth import save_or_update_twitch_tokens
from bot.frontend.helpers.auth import get_twitch_user
from bot.frontend.helpers.auth_constents import JWT_ALG
from bot.frontend.helpers.auth_constents import JWT_EXPIRY_DAYS
from bot.frontend.helpers.auth_constents import TWITCH_SCOPES
from bot.helpers.app_context import APP_CONTEXT
from bot.helpers.log import LogLevel
from bot.helpers.log import LogProgram
from bot.helpers.log import log_default
from bot.helpers.log import log_exception
from bot.types.twitch_user_info import TwitchUserInfo

router: Final = APIRouter(prefix="/auth")
TWITCH_OAUTH_STATE_COOKIE_KEY: Final = "TWITCH_OAUTH_STATE_COOKIE"


@router.get("/twitch")
async def auth_twitch() -> RedirectResponse:
    state = secrets.token_urlsafe(32)

    params = {
        "client_id": APP_CONTEXT.twitch_client_id.value_or_rise(),
        "redirect_uri": APP_CONTEXT.twitch_redirect_uri.value(),
        "response_type": "code",
        "scope": " ".join([s.value for s in TWITCH_SCOPES]),
        "state": state,
    }
    url = f"https://id.twitch.tv/oauth2/authorize?{urlencode(params)}"
    response = RedirectResponse(url, status_code=HTTPStatus.FOUND)
    response.set_cookie(
        key=TWITCH_OAUTH_STATE_COOKIE_KEY,
        value=state,
        max_age=600,
        httponly=True,
        secure=APP_CONTEXT.environment_state.value().is_production(),
        samesite="lax",
        path="/auth/twitch",
    )
    return response


@router.get("/twitch/callback")
async def auth_twitch_callback(request: Request, code: Optional[str], state: Optional[str]) -> RedirectResponse:
    expected_state: Final = request.cookies.get(TWITCH_OAUTH_STATE_COOKIE_KEY)
    if expected_state is None or state is None or code is None or expected_state != state:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="OAuth state missmatch or missing code")

    try:

        async def _do_login() -> str:
            twitch: Final = await Twitch(
                APP_CONTEXT.twitch_client_id.value_or_rise(),
                APP_CONTEXT.twitch_credentials.value_or_rise(),
                authenticate_app=False,
            )
            try:
                auth: Final = UserAuthenticator(twitch, TWITCH_SCOPES, url=APP_CONTEXT.twitch_redirect_uri.value())
                auth_result: Final = await auth.authenticate(user_token=code)  # type: ignore[reportUnknownVariableType]
                if auth_result is None:
                    raise HTTPException(
                        status_code=HTTPStatus.UNAUTHORIZED, detail="Failed to authenticate with Twitch"
                    )
                access_token, refresh_token = cast(tuple[str, str], auth_result)
                await twitch.set_user_authentication(access_token, TWITCH_SCOPES, refresh_token, validate=True)
                user: Final = await first(twitch.get_users())
                if user is None:
                    raise HTTPException(
                        status_code=HTTPStatus.UNAUTHORIZED, detail="Failed to receive user information from Twitch"
                    )

                now: Final = datetime.now(UTC)
                expires_at: Final = now + timedelta(days=JWT_EXPIRY_DAYS)
                expires_at_timestamp: Final = int(expires_at.timestamp())

                result = save_or_update_twitch_tokens(user.id, access_token, refresh_token, expires_at_timestamp)
                if not result:
                    raise HTTPException(
                        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                        detail="Failed to save twitch tokens to a database",
                    )

                payload: Final = {
                    "sub": user.id,
                    "login": user.login,
                    "display_name": user.display_name,
                    "profile_image_url": user.profile_image_url,
                    "exp": expires_at_timestamp,
                    "iat": int(now.timestamp()),
                }
                log_default(
                    LogLevel.INFO,
                    f"Twitch user {user.id}({user.display_name}) logged in successfully | login: {user.login}",
                )
                session_jwt: Final = jwt.encode(  # type: ignore[reportUnknownMemberType]
                    payload,
                    APP_CONTEXT.jwt_secret.value(),
                    algorithm=JWT_ALG,
                )
                return session_jwt
            finally:
                await twitch.close()

        session_jwt: Final = await _do_login()
        return_response = RedirectResponse(url="/", status_code=HTTPStatus.SEE_OTHER)
        return_response.delete_cookie(TWITCH_OAUTH_STATE_COOKIE_KEY)
        return_response.set_cookie(
            key="TWITCH_SESSION_COOKIE",
            value=session_jwt,
            max_age=JWT_EXPIRY_DAYS * 60 * 60 * 24,
            httponly=True,
            secure=APP_CONTEXT.environment_state.value().is_production(),
            samesite="lax",
            path="/",
        )
        return return_response

    except Exception as e:
        log_exception(e, LogProgram.Default, "Error during Twitch OAuth Callback")
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail="Error during Twitch OAuth Callback"
        ) from e


@router.get("discord")
async def auth_discord() -> RedirectResponse:
    return RedirectResponse(url="/")


@router.get("discord/callback")
async def auth_discord_callback(request: Request) -> RedirectResponse:
    return RedirectResponse(url="/")


@router.get("/logout")
async def logout(
    current_twitch_user: Annotated[Optional[TwitchUserInfo], Depends(get_twitch_user)],
) -> RedirectResponse:
    if current_twitch_user is not None:
        token_set = get_twitch_tokens(current_twitch_user.id_)
        if token_set is not None:
            try:
                await revoke_token(
                    APP_CONTEXT.twitch_client_id.value_or_rise(),
                    token_set.access_token,
                )
                log_default(LogLevel.INFO, f"Twitch user {current_twitch_user.id_} logged out successfully")
            except Exception as e:
                log_default(LogLevel.ERROR, f"Failed to revoke Twitch token for user {current_twitch_user.id_}")
                log_exception(
                    e, LogProgram.Default, f"Failed to revoke Twitch token for user {current_twitch_user.id_}"
                )

        result = delete_twitch_tokens(current_twitch_user.id_)
        if not result:
            log_default(LogLevel.ERROR, f"Failed to delete twitch tokens for user {current_twitch_user.id_}")

    response = RedirectResponse(url="/")
    response.delete_cookie("TWITCH_SESSION_COOKIE", path="/")
    return response
