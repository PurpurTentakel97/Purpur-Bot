from typing import Optional

from twitchAPI.twitch import Twitch
from twitchAPI.type import AuthScope

from bot.core.app_context import APP_CONTEXT
from bot.core.twitch_broadcast_auth import get_broadcast_tokens
from bot.core.twitch_broadcast_auth import store_or_update_broadcast_tokens
from bot.helpers.log import LogLevel
from bot.helpers.log import log_twitch


class TwitchBroadcastClientFactory:
    def __init__(self) -> None:
        self._clients: dict[tuple[int, str], Twitch] = {}
        self._scopes = [AuthScope.CHANNEL_MANAGE_BROADCAST, AuthScope.CHANNEL_READ_SUBSCRIPTIONS]

    async def get_client(self, bot_id: int, channel_name: str) -> Optional[Twitch]:
        key = (bot_id, channel_name)
        if key in self._clients:
            return self._clients[key]

        result = get_broadcast_tokens(bot_id, channel_name)
        if result.state.fail or result.value is None:
            log_twitch(LogLevel.DEBUG, f"No broadcast tokens found for bot {bot_id} and channel {channel_name}")
            return None

        tokens = result.value

        async def _refresh_callback(new_access_token: str, new_refresh_token: str) -> None:
            # We don't have the expires_at here directly from the callback,
            # but usually it's around 4 hours.
            # For simplicity, we might just set it to a future timestamp or use a default.
            # However, the twitchAPI usually provides it if we use the right flow.
            # If we don't have it, we might need to be careful.
            # Looking at TwitchClient implementation, it doesn't seem to store expires_at.
            # Wait, TwitchClient.create's _user_user_refresh only takes 2 args.
            import time

            expires_at = int(time.time()) + 3600  # default 1 hour
            store_or_update_broadcast_tokens(
                bot_id, channel_name, tokens.twitch_user_id, new_access_token, new_refresh_token, expires_at
            )

        try:
            client = await Twitch(
                APP_CONTEXT.twitch_client_id.value_or_rise(),
                APP_CONTEXT.twitch_credentials.value_or_rise(),
            )
            client.user_auth_refresh_callback = _refresh_callback

            await client.set_user_authentication(tokens.access_token, self._scopes, tokens.refresh_token, validate=True)

            self._clients[key] = client
            return client
        except Exception as e:
            log_twitch(LogLevel.ERROR, f"Failed to initialize broadcast client for {channel_name}: {e}")
            return None

    async def close_all(self) -> None:
        for client in self._clients.values():
            await client.close()
        self._clients.clear()


TWITCH_BROADCAST_CLIENT_FACTORY = TwitchBroadcastClientFactory()
