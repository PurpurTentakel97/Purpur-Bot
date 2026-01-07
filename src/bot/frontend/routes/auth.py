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

import httpx
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

from bot.core.app_context import APP_CONTEXT
from bot.database.twitch_auth import delete_discord_tokens
from bot.database.twitch_auth import delete_twitch_tokens
from bot.database.twitch_auth import select_discord_tokens
from bot.database.twitch_auth import save_or_update_discord_tokens
from bot.database.twitch_auth import save_or_update_twitch_tokens
from bot.database.twitch_auth import select_twitch_tokens
from bot.frontend.helpers.auth import get_discord_user
from bot.frontend.helpers.auth import get_twitch_user
from bot.frontend.helpers.auth_constents import DISCORD_SCOPES
from bot.frontend.helpers.auth_constents import JWT_ALG
from bot.frontend.helpers.auth_constents import JWT_EXPIRY_DAYS
from bot.frontend.helpers.auth_constents import TWITCH_SCOPES
from bot.frontend.types.discord_session_cookie_jwt import DiscordSessionCookie
from bot.frontend.types.discord_user_info import DiscordUserInfo
from bot.frontend.types.twitch_session_cookie_jwt import TwitchSessionCookie
from bot.frontend.types.twitch_user_info import TwitchUserInfo
from bot.helpers.log import LogLevel
from bot.helpers.log import LogProgram
from bot.helpers.log import log_default
from bot.helpers.log import log_exception

router: Final = APIRouter(prefix="/auth")
TWITCH_OAUTH_STATE_COOKIE_KEY: Final = "TWITCH_OAUTH_STATE_COOKIE"
DISCORD_OAUTH_STATE_COOKIE_KEY: Final = "DISCORD_OAUTH_STATE_COOKIE"


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

                payload = TwitchSessionCookie(
                    user_id=user.id,
                    login=user.login,
                    display_name=user.display_name,
                    profile_image_url=user.profile_image_url,
                    exp=expires_at_timestamp,
                    iat=int(now.timestamp()),
                )
                log_default(
                    LogLevel.INFO,
                    f"Twitch user {user.id}({user.display_name}) logged in successfully | login: {user.login}",
                )
                session_jwt: Final = jwt.encode(  # type: ignore[reportUnknownMemberType]
                    payload.model_dump(),
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


@router.get("/discord")
async def auth_discord() -> RedirectResponse:
    state = secrets.token_urlsafe(32)

    params = {
        "client_id": APP_CONTEXT.discord_client_id.value_or_rise(),
        "redirect_uri": APP_CONTEXT.discord_redirect_uri.value(),
        "response_type": "code",
        "scope": " ".join(DISCORD_SCOPES),
        "state": state,
    }
    url = f"https://discord.com/api/oauth2/authorize?{urlencode(params)}"
    response = RedirectResponse(url, status_code=HTTPStatus.FOUND)
    response.set_cookie(
        key=DISCORD_OAUTH_STATE_COOKIE_KEY,
        value=state,
        max_age=600,
        httponly=True,
        secure=APP_CONTEXT.environment_state.value().is_production(),
        samesite="lax",
        path="/auth/discord",
    )
    return response


@router.get("/discord/callback")
async def auth_discord_callback(
    request: Request, code: Optional[str] = None, state: Optional[str] = None
) -> RedirectResponse:
    expected_state: Final = request.cookies.get(DISCORD_OAUTH_STATE_COOKIE_KEY)
    if expected_state is None or state is None or code is None or expected_state != state:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="OAuth state missmatch or missing code")

    try:

        async def _do_login() -> str:
            async with httpx.AsyncClient() as client:
                # Exchange code for token
                token_url = "https://discord.com/api/oauth2/token"
                data = {
                    "client_id": APP_CONTEXT.discord_client_id.value_or_rise(),
                    "client_secret": APP_CONTEXT.discord_client_secret.value_or_rise(),
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": APP_CONTEXT.discord_redirect_uri.value(),
                }
                headers = {"Content-Type": "application/x-www-form-urlencoded"}
                token_response = await client.post(token_url, data=data, headers=headers)
                token_response.raise_for_status()
                token_data = token_response.json()

                access_token = token_data["access_token"]
                refresh_token = token_data.get("refresh_token", "")
                expires_in = token_data.get("expires_in", 0)

                # Fetch user info
                user_url = "https://discord.com/api/users/@me"
                user_headers = {"Authorization": f"Bearer {access_token}"}
                user_response = await client.get(user_url, headers=user_headers)
                user_response.raise_for_status()
                user_data = user_response.json()

                user_id = user_data["id"]
                username = user_data["username"]
                global_name = user_data.get("global_name") or username
                avatar = user_data.get("avatar")
                if avatar:
                    avatar_url = f"https://cdn.discordapp.com/avatars/{user_id}/{avatar}.png"
                else:
                    avatar_url = f"https://cdn.discordapp.com/embed/avatars/{int(user_id) % 5}.png"

                now: Final = datetime.now(UTC)
                expires_at: Final = now + timedelta(seconds=expires_in)
                expires_at_timestamp: Final = int(expires_at.timestamp())

                result = save_or_update_discord_tokens(user_id, access_token, refresh_token, expires_at_timestamp)
                if not result:
                    raise HTTPException(
                        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                        detail="Failed to save discord tokens to a database",
                    )

                payload = DiscordSessionCookie(
                    user_id=user_id,
                    username=username,
                    display_name=global_name,
                    avatar_url=avatar_url,
                    exp=int((now + timedelta(days=JWT_EXPIRY_DAYS)).timestamp()),
                    iat=int(now.timestamp()),
                )
                log_default(
                    LogLevel.INFO,
                    f"Discord user {user_id}({global_name}) logged in successfully | login: {username}",
                )
                session_jwt: Final = jwt.encode(  # type: ignore[reportUnknownMemberType]
                    payload.model_dump(),
                    APP_CONTEXT.jwt_secret.value(),
                    algorithm=JWT_ALG,
                )
                return session_jwt

        session_jwt: Final = await _do_login()
        return_response = RedirectResponse(url="/", status_code=HTTPStatus.SEE_OTHER)
        return_response.delete_cookie(DISCORD_OAUTH_STATE_COOKIE_KEY)
        return_response.set_cookie(
            key="DISCORD_SESSION_COOKIE",
            value=session_jwt,
            max_age=JWT_EXPIRY_DAYS * 60 * 60 * 24,
            httponly=True,
            secure=APP_CONTEXT.environment_state.value().is_production(),
            samesite="lax",
            path="/",
        )
        return return_response

    except Exception as e:
        log_exception(e, LogProgram.Default, "Error during Discord OAuth Callback")
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail="Error during Discord OAuth Callback"
        ) from e


@router.get("/logout")
async def logout(
    current_twitch_user: Annotated[Optional[TwitchUserInfo], Depends(get_twitch_user)],
    current_discord_user: Annotated[Optional[DiscordUserInfo], Depends(get_discord_user)],
) -> RedirectResponse:
    if current_twitch_user is not None:
        token_set = select_twitch_tokens(current_twitch_user.id_)
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

    if current_discord_user is not None:
        token_set = select_discord_tokens(current_discord_user.id_)
        if token_set is not None:
            try:
                async with httpx.AsyncClient() as client:
                    revoke_url = "https://discord.com/api/oauth2/token/revoke"
                    data = {
                        "client_id": APP_CONTEXT.discord_client_id.value_or_rise(),
                        "client_secret": APP_CONTEXT.discord_client_secret.value_or_rise(),
                        "token": token_set.access_token,
                    }
                    headers = {"Content-Type": "application/x-www-form-urlencoded"}
                    await client.post(revoke_url, data=data, headers=headers)
                log_default(LogLevel.INFO, f"Discord user {current_discord_user.id_} logged out and token revoked")
            except Exception as e:
                log_default(LogLevel.ERROR, f"Failed to revoke Discord token for user {current_discord_user.id_}")
                log_exception(
                    e, LogProgram.Default, f"Failed to revoke Discord token for user {current_discord_user.id_}"
                )

        result = delete_discord_tokens(current_discord_user.id_)
        if not result:
            log_default(LogLevel.ERROR, f"Failed to delete discord tokens for user {current_discord_user.id_}")

    response = RedirectResponse(url="/")
    response.delete_cookie("TWITCH_SESSION_COOKIE", path="/")
    response.delete_cookie("DISCORD_SESSION_COOKIE", path="/")
    return response
