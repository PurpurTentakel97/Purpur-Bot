from typing import Final
from typing import Optional
from typing import Self
from typing import cast

from twitchAPI.oauth import UserAuthenticator
from twitchAPI.twitch import Twitch
from twitchAPI.type import AuthScope

from bot.helpers.log import log_twitch, LogLevel


class TwitchClient:
    def __init__(self, client: Twitch) -> None:
        self.client = client
        log_twitch(LogLevel.INFO, "Twitch client is ready!")

    @classmethod
    async def create(cls, app_id: str, credentials: str) -> Self:
        log_twitch(LogLevel.INFO, "Connecting in to Twitch...")
        user_scope = [AuthScope.CHAT_READ, AuthScope.CHAT_EDIT]
        twitch = await Twitch(app_id, credentials)
        auth: Final = UserAuthenticator(twitch, user_scope)

        # this cast is needed because the lib does not provide a proper type hint for the result
        # however, the documentation ensures that the result is a tuple of two strings or None
        result: Final = cast(Optional[tuple[str, str]], await auth.authenticate())
        assert result is not None

        token, refresh_token = result

        await twitch.set_user_authentication(token, user_scope, refresh_token)

        return cls(twitch)
