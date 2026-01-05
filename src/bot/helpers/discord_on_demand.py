from bot.chat.discord_server import DiscordServer
from bot.types.feature_flag import DEFAULT_DISCORD_FEATURES
from bot.types.programm_parts import PROGRAMM_PARTS


async def start_single_discord_bot(id_: int, server_id: int) -> bool:
    if PROGRAMM_PARTS.discord is None:
        return False

    discord_server = DiscordServer(id_, server_id, DEFAULT_DISCORD_FEATURES)
    PROGRAMM_PARTS.discord.connect_server(discord_server)

    return True


async def stop_single_discord_bot(id_: int, server_id: int) -> bool:
    if PROGRAMM_PARTS.discord is None:
        return False

    for server in PROGRAMM_PARTS.discord.servers:
        if server.id == id_ and server.server_id == server_id:
            PROGRAMM_PARTS.discord.remove_server(server)
            await PROGRAMM_PARTS.discord.leave_guild(server_id)
            return True

    return False
