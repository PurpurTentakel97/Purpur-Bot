from bot.core.types.programm_parts import PROGRAMM_PARTS


async def _stop_discord_bot() -> None:
    if PROGRAMM_PARTS.discord is None:
        return

    await PROGRAMM_PARTS.discord.terminate()


async def _stop_twitch_bot() -> None:
    if PROGRAMM_PARTS.twitch is None:
        return

    await PROGRAMM_PARTS.twitch.terminate()


async def _stop_twitch_event_hub() -> None:
    if PROGRAMM_PARTS.event_hub is None:
        return
    await PROGRAMM_PARTS.event_hub.terminate()


def _stop_database() -> None:
    PROGRAMM_PARTS.database.close()


def _stop_broadcast() -> None:
    if PROGRAMM_PARTS.broadcast is None:
        return

    PROGRAMM_PARTS.broadcast.cleanup()


async def terminate_programm() -> None:
    await _stop_twitch_event_hub()
    await _stop_discord_bot()
    await _stop_twitch_bot()
    _stop_database()
    _stop_broadcast()
    # no need to terminate the cooldowns
