from typing import List
from twitchAPI.twitch import Twitch
from bot.helpers.app_context import APP_CONTEXT
from bot.database.auth import get_twitch_tokens
from bot.frontend.helpers.auth_constents import TWITCH_SCOPES
from bot.helpers.log import log_exception, LogProgram


async def get_allowed_twitch_channels(user_id: str, user_login: str) -> List[str]:
    tokens = get_twitch_tokens(user_id)
    if tokens is None:
        return [user_login]

    twitch = await Twitch(
        APP_CONTEXT.twitch_client_id.value_or_rise(),
        APP_CONTEXT.twitch_credentials.value_or_rise(),
        authenticate_app=False,
    )

    try:
        await twitch.set_user_authentication(
            tokens.access_token,
            TWITCH_SCOPES,
            tokens.refresh_token,
            validate=True
        )

        channels = [user_login]

        async for channel in twitch.get_moderated_channels(user_id):
            channels.append(channel.broadcaster_login)

        return sorted(set(channels))
    except Exception as e:
        log_exception(e, LogProgram.Default, f"Failed to get allowed twitch channels for user {user_id}")
        return [user_login]
    finally:
        await twitch.close()
