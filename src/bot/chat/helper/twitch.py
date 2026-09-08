from twitchAPI.helper import first
from twitchAPI.object.api import TwitchUser
from twitchAPI.type import TwitchAPIException

from bot.core.types.programm_parts import PROGRAMM_PARTS
from bot.core.types.result import Result
from bot.core.types.result import ResultState
from bot.helpers.log import LogProgram
from bot.helpers.log import log_exception


async def get_user_by_id(user_id: str) -> Result[TwitchUser]:
    if PROGRAMM_PARTS.twitch is None:
        return Result(ResultState.ERROR, None)

    try:
        # `OSError` also covers request timeouts and connection failures from the underlying aiohttp session.
        user = await first(PROGRAMM_PARTS.twitch.client.get_users(user_ids=[user_id]))
    except (TwitchAPIException, OSError) as exception:
        log_exception(exception, LogProgram.Twitch, f"failed to look up twitch user by id | id={user_id!r}")
        return Result(ResultState.ERROR, None)

    if user is None:
        return Result(ResultState.USER_NOT_FOUND, None)

    return Result(ResultState.SUCCESS, user)


async def get_user_by_name(user_name: str) -> Result[TwitchUser]:
    if PROGRAMM_PARTS.twitch is None:
        return Result(ResultState.ERROR, None)

    try:
        # `OSError` also covers request timeouts and connection failures from the underlying aiohttp session.
        user = await first(PROGRAMM_PARTS.twitch.client.get_users(logins=[user_name]))
    except (TwitchAPIException, OSError) as exception:
        log_exception(exception, LogProgram.Twitch, f"failed to look up twitch user by name | name={user_name!r}")
        return Result(ResultState.ERROR, None)

    if user is None:
        return Result(ResultState.USER_NOT_FOUND, None)

    return Result(ResultState.SUCCESS, user)
