from typing import Optional

from bot.discord_bot.discord_client import DiscordClient
from bot.twitch_bot.twitch_client import TwitchClient
from bot.types.programm_parts import ProgramParts


async def _stop_discord_bot(discord_client: Optional[DiscordClient]) -> None:
    if discord_client is None:
        return

    await discord_client.terminate()


async def _stop_twitch_bot(twitch_client: Optional[TwitchClient]) -> None:
    if twitch_client is None:
        return

    await twitch_client.terminate()


async def terminate_programm(program: ProgramParts) -> None:
    await _stop_discord_bot(program.discord)
    await _stop_twitch_bot(program.twitch)
