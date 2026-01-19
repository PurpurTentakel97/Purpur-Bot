from datetime import datetime
from datetime import timedelta
from typing import Final

from twitchAPI.twitch import Twitch

from bot.core.app_context import APP_CONTEXT
from bot.core.twitch_auth import get_twitch_tokens as get_twitch_tokens_core
from bot.frontend.helpers.auth_constents import TWITCH_SCOPES
from bot.helpers.log import LogProgram
from bot.helpers.log import log_exception

TWITCH_CHANNELS_CACHE: Final[dict[str, tuple[list[str], datetime]]] = {}


async def get_allowed_twitch_channels(user_id: str, user_login: str) -> list[str]:
    if user_id in TWITCH_CHANNELS_CACHE:
        channels, timestamp = TWITCH_CHANNELS_CACHE[user_id]
        if datetime.now() - timestamp < timedelta(minutes=5):
            return channels

    tokens = get_twitch_tokens_core(user_id)
    if tokens.value is None:
        return [user_login]

    twitch = await Twitch(
        APP_CONTEXT.twitch_client_id.value_or_rise(),
        APP_CONTEXT.twitch_credentials.value_or_rise(),
        authenticate_app=False,
    )

    try:
        await twitch.set_user_authentication(
            tokens.value.access_token, TWITCH_SCOPES, tokens.value.refresh_token, validate=True
        )

        channels = [user_login]

        async for channel in twitch.get_moderated_channels(user_id):
            channels.append(channel.broadcaster_login)

        allowed_channels: Final = sorted(set(channels))
        TWITCH_CHANNELS_CACHE[user_id] = (allowed_channels, datetime.now())
        return allowed_channels

    except Exception as e:
        log_exception(e, LogProgram.Default, f"Failed to get allowed twitch channels for user {user_id}")
        return [user_login]
    finally:
        await twitch.close()
