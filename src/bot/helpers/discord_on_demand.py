from bot.chat.discord_server import DiscordServer
from bot.types.feature_flag import DEFAULT_DISCORD_FEATURES
from bot.types.programm_parts import PROGRAMM_PARTS


async def start_single_discord_bot(id_: int, server_id: int) -> bool:
    if PROGRAMM_PARTS.discord is None:
        return False

    discord_server = DiscordServer(id_, server_id, DEFAULT_DISCORD_FEATURES)
    PROGRAMM_PARTS.discord.connect_chat(discord_server)

    return True


async def stop_single_discord_bot(id_: int, server_id: int) -> bool:
    if PROGRAMM_PARTS.discord is None:
        return False

    # if server_id in PROGRAMM_PARTS.discord._servers:  # type: ignore[reportPrivateUsage]
    #    del PROGRAMM_PARTS.discord._servers[server_id]  # type: ignore[reportPrivateUsage]
    #    return True

    return False
