from typing import NamedTuple
from typing import Optional
from typing import Self
from typing import final

from bot.core.helpers.env import get_env_var_or_default


@final
class TwitchTokens(NamedTuple):
    access_token: str
    refresh_token: str

    @classmethod
    def try_load_from_env(cls) -> Optional[Self]:
        access_token = get_env_var_or_default("TWITCH_ACCESS_TOKEN", None)
        refresh_token = get_env_var_or_default("TWITCH_REFRESH_TOKEN", None)

        if access_token is None or refresh_token is None:
            return None
        return cls(access_token, refresh_token)
