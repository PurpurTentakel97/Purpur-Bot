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
from twitchAPI.type import TwitchAPIException
from twitchAPI.type import TwitchAuthorizationException
from twitchAPI.type import UnauthorizedException

from bot.core.app_context import APP_CONTEXT
from bot.helpers.log import LogLevel
from bot.helpers.log import LogProgram
from bot.helpers.log import log_exception
from bot.helpers.log import log_twitch


class TwitchClient:
    _SCOPES = [AuthScope.CHAT_READ, AuthScope.CHAT_EDIT, AuthScope.CHANNEL_MANAGE_BROADCAST]

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

    async def send_change_title(self, message: ChatMessage, broadcast_id: str, new_title: str) -> None:
        try:
            await self.client.modify_channel_information(broadcaster_id=broadcast_id, title=new_title)
            await message.sender_chat.send_response([message.to_response_message(f"Title changed to '{new_title}'")])
        except TwitchAPIException as e:
            log_exception(e, LogProgram.Twitch, f"Failed to change title of {broadcast_id}")
            await message.sender_chat.send_response([message.to_response_message(f"Failed to change title: {e}")])

    async def send_change_game(self, message: ChatMessage, broadcast_id: str, new_game: str) -> None:
        try:
            game_id: Optional[str] = None

            async for game in self.client.get_games(names=[new_game]):
                game_id = game.id
                break

            if not game_id:
                raise TwitchAPIException(f"Game '{new_game}' not found")

            await self.client.modify_channel_information(broadcaster_id=broadcast_id, game_id=game_id)

            await message.sender_chat.send_response([message.to_response_message(f"Game changed to '{new_game}'")])

        except TwitchAPIException as e:
            log_exception(e, LogProgram.Twitch, f"Failed to change game of {broadcast_id}")
            await message.sender_chat.send_response([message.to_response_message(f"Failed to change game: {e}")])

    async def send_change_category(self, message: ChatMessage, broadcast_id: str, new_tags: list[str]) -> None:
        try:
            pass
        except TwitchAPIException as e:
            log_exception(e, LogProgram.Twitch, f"Failed to change category of {broadcast_id}")
            await message.sender_chat.send_response([message.to_response_message(f"Failed to change category: {e}")])
