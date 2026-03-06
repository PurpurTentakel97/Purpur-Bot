import re
import typing

import discord

from bot.core.types.programm_parts import PROGRAMM_PARTS
from bot.core.types.result import Result
from bot.core.types.result import ResultState
from bot.helpers.log import LogLevel
from bot.helpers.log import log_default

ROLE_PATTERN = re.compile(r"@([^\s@]+)")


def replace_role_mentions(server_id: int, text: str) -> Result[str]:
    if not PROGRAMM_PARTS.discord:
        log_default(LogLevel.WARNING, "Discord isn't initialized while resolving roles. Skipping...")
        return Result(ResultState.UNABLE_TO_EXTRACT_ROLE, text)

    guild = PROGRAMM_PARTS.discord.get_guild(server_id)
    if not guild:
        log_default(LogLevel.WARNING, f"Discord guild {server_id} not found while resolving roles. Skipping...")
        return Result(ResultState.UNABLE_TO_EXTRACT_ROLE, text)

    unhandled_roles: list[str] = []

    def replace(match: typing.Match[str]) -> str:
        role_name = match.group(1)
        role = discord.utils.get(guild.roles, name=role_name)

        if role:
            return role.mention

        unhandled_roles.append(role_name)
        return match.group(0)

    result_text = ROLE_PATTERN.sub(replace, text)

    if unhandled_roles:
        log_default(LogLevel.WARNING, f"Roles not found in guild {server_id}: {', '.join(unhandled_roles)}")
        return Result(ResultState.UNABLE_TO_EXTRACT_ROLE, result_text)

    return Result(ResultState.SUCCESS, result_text)
