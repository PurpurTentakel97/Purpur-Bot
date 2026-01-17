from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Final
from typing import Optional
from typing import Self
from typing import cast

from bot.chat.types.message import ChatMessage

if TYPE_CHECKING:
    from bot.chat.twitch_chat import TwitchChat

from twitchAPI.oauth import UserAuthenticator
from twitchAPI.twitch import Twitch
from twitchAPI.type import AuthScope
from twitchAPI.type import InvalidRefreshTokenException
from twitchAPI.type import TwitchAuthorizationException
from twitchAPI.type import UnauthorizedException

from bot.core.app_context import APP_CONTEXT
from bot.helpers.log import LogLevel
from bot.helpers.log import log_twitch


class TwitchClient:
    _SCOPES = [AuthScope.CHAT_READ, AuthScope.CHAT_EDIT]

    def __init__(self, client: Twitch) -> None:
        self.client = client
        self._chats: list[TwitchChat] = []
        log_twitch(LogLevel.INFO, "Twitch client is ready!")

    async def get_next_message(self) -> Optional[ChatMessage]:
        for chat in self._chats:
            message = await chat.get_next_message()
            if message is not None:
                return message
        return None

    @property
    def chats(self) -> list[TwitchChat]:
        return self._chats

    def connect_chat(self, chat: TwitchChat) -> None:
        self._chats.append(chat)

    def disconnect_chat(self, chat: TwitchChat) -> None:
        self._chats.remove(chat)

    async def terminate(self) -> None:
        for chat in self._chats:
            await chat.terminate(self)
        await self.client.close()
        log_twitch(LogLevel.INFO, "Twitch client terminated.")

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

        twitch: Optional[Twitch] = None
        try:
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

            await twitch.set_user_authentication(access_token, cls._SCOPES, refresh_token, validate=True)
        except (InvalidRefreshTokenException, UnauthorizedException):
            log_twitch(LogLevel.ERROR, "Invalid refresh token: try to reauthenticate...")
            try:
                assert twitch is not None
                access_token, refresh_token = await _new_tokens(twitch)
                await twitch.set_user_authentication(access_token, cls._SCOPES, refresh_token, validate=True)
            except (InvalidRefreshTokenException, UnauthorizedException) as e:
                log_twitch(LogLevel.ERROR, f"Twitch authentication failed: {e}")
                return None
        except (Exception, TwitchAuthorizationException) as e:
            log_twitch(LogLevel.ERROR, f"Twitch connection failed: {e}")
            return None

        assert twitch is not None
        return cls(twitch)
