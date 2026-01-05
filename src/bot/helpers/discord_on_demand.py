from bot.types.programm_parts import PROGRAMM_PARTS


async def start_single_discord_bot(id_: int, server_id: int) -> bool:
    if PROGRAMM_PARTS.discord is None:
        return False

    return False


async def stop_single_discord_bot(id_: int, server_id: int) -> bool:
    if PROGRAMM_PARTS.discord is None:
        return False
    return False
