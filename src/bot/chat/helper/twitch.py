from twitchAPI.helper import first
from twitchAPI.object.api import TwitchUser

from bot.core.types.programm_parts import PROGRAMM_PARTS
from bot.core.types.result import Result
from bot.core.types.result import ResultState


async def get_user_by_id(user_id: str) -> Result[TwitchUser]:
    if PROGRAMM_PARTS.twitch is None:
        return Result(ResultState.ERROR, None)

    user = await first(PROGRAMM_PARTS.twitch.client.get_users(user_ids=[user_id]))
    if user is None:
        return Result(ResultState.USER_NOT_FOUND, None)

    return Result(ResultState.SUCCESS, user)


async def get_user_by_name(user_name: str) -> Result[TwitchUser]:
    if PROGRAMM_PARTS.twitch is None:
        return Result(ResultState.ERROR, None)

    user = await first(PROGRAMM_PARTS.twitch.client.get_users(logins=[user_name]))
    if user is None:
        return Result(ResultState.USER_NOT_FOUND, None)

    return Result(ResultState.SUCCESS, user)
