from bot.types.core.programm_parts import PROGRAMM_PARTS


async def _stop_discord_bot() -> None:
    if PROGRAMM_PARTS.discord is None:
        return

    await PROGRAMM_PARTS.discord.terminate()


async def _stop_twitch_bot() -> None:
    if PROGRAMM_PARTS.twitch is None:
        return

    await PROGRAMM_PARTS.twitch.terminate()


def _stop_database() -> None:
    PROGRAMM_PARTS.database.close()


async def terminate_programm() -> None:
    await _stop_discord_bot()
    await _stop_twitch_bot()
    _stop_database()
