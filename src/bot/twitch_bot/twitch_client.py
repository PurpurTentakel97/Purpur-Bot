from typing import Final
from typing import Optional
from typing import Self
from typing import cast

from twitchAPI.oauth import UserAuthenticator
from twitchAPI.twitch import Twitch
from twitchAPI.type import AuthScope
from twitchAPI.type import InvalidRefreshTokenException
from twitchAPI.type import UnauthorizedException

from bot.helpers.app_context import APP_CONTEXT
from bot.helpers.log import LogLevel
from bot.helpers.log import log_twitch


class TwitchClient:
    _SCOPES = [AuthScope.CHAT_READ, AuthScope.CHAT_EDIT]

    def __init__(self, client: Twitch) -> None:
        self.client = client
        log_twitch(LogLevel.INFO, "Twitch client is ready!")

    @classmethod
    async def create(cls) -> Optional[Self]:
        if not APP_CONTEXT.twitch_client_id.is_valid() or not APP_CONTEXT.twitch_credentials.is_valid():
            log_twitch(
                LogLevel.ERROR, "Twitch credentials are not found in environment variables. Twitch Bot isn't started."
            )
            return None

        log_twitch(LogLevel.INFO, "Connecting in to Twitch...")

        async def _user_user_refresh(new_access_token: str, new_refresh_token: str) -> None:
            APP_CONTEXT.update_twitch_tokens(new_access_token, new_refresh_token)

        async def _new_tokens(twitch: Twitch) -> tuple[str, str]:  # access_token, refresh_token
            auth: Final = UserAuthenticator(twitch, cls._SCOPES)
            # this cast is needed because the lib does not provide a proper type hint for the result
            # however, the documentation ensures that the result is a tuple of two strings or None
            auth_response: Final = cast(Optional[tuple[str, str]], await auth.authenticate())
            assert auth_response is not None
            access_token, refresh_token = auth_response
            APP_CONTEXT.update_twitch_tokens(access_token, refresh_token)
            return access_token, refresh_token

        if APP_CONTEXT.twitch_tokens.is_valid():
            access_token, refresh_token = APP_CONTEXT.twitch_tokens.value_or_rise()
            twitch = await Twitch(
                APP_CONTEXT.twitch_client_id.value_or_rise(),
                APP_CONTEXT.twitch_credentials.value_or_rise(),
                authenticate_app=False,
            )
            twitch.user_auth_refresh_callback = _user_user_refresh

        else:
            twitch = await Twitch(
                APP_CONTEXT.twitch_client_id.value_or_rise(), APP_CONTEXT.twitch_credentials.value_or_rise()
            )
            twitch.user_auth_refresh_callback = _user_user_refresh
            access_token, refresh_token = await _new_tokens(twitch)

        try:
            await twitch.set_user_authentication(access_token, cls._SCOPES, refresh_token, validate=True)
        except (InvalidRefreshTokenException, UnauthorizedException):
            log_twitch(LogLevel.ERROR, "Invalid refresh token: try to reauthenticate...")
            access_token, refresh_token = await _new_tokens(twitch)
            await twitch.set_user_authentication(access_token, cls._SCOPES, refresh_token, validate=True)

        return cls(twitch)
