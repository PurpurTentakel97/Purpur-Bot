import discord

from bot.core.types.programm_parts import PROGRAMM_PARTS
from bot.core.types.result import Result
from bot.core.types.result import ResultState


async def get_user_by_id(user_id: int) -> Result[discord.User]:
    if PROGRAMM_PARTS.discord is None:
        return Result(ResultState.ERROR, None)

    try:
        user = await PROGRAMM_PARTS.discord.fetch_user(user_id)
        return Result(ResultState.SUCCESS, user)
    except Exception:
        return Result(ResultState.USER_NOT_FOUND, None)


async def get_user_by_name(user_name: str) -> Result[discord.User]:
    if PROGRAMM_PARTS.discord is None:
        return Result(ResultState.ERROR, None)

    # discord.py doesn't have a direct fetch_user_by_name, so we look through guilds
    # or just use the internal cache if available.
    # fetch_user only works by ID.
    # For now, we'll try to find the user in the client's internal user cache.

    user = discord.utils.get(PROGRAMM_PARTS.discord.users, name=user_name)
    if user is None:
        return Result(ResultState.USER_NOT_FOUND, None)

    return Result(ResultState.SUCCESS, user)
