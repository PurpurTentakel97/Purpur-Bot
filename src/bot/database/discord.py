from typing import Optional

from bot.core.types.programm_parts import PROGRAMM_PARTS
from bot.database.types.discord_server import DiscordServerDB

TABLE_NAME = "bot_discord_lookup"


def select_discord_servers_by_bot_id(bot_id: int) -> list[DiscordServerDB]:
    return PROGRAMM_PARTS.database.select_all(table_name=TABLE_NAME, where={"bot_id": bot_id}, type_=DiscordServerDB)


async def insert_discord_server(bot_id: int, server_id: int, server_name: str) -> Optional[int]:
    return PROGRAMM_PARTS.database.insert(
        table_name=TABLE_NAME, data={"bot_id": bot_id, "server_id": server_id, "server_name": server_name}
    )


async def delete_discord_server(bot_id: int, server_id: int) -> bool:
    return PROGRAMM_PARTS.database.delete(table_name=TABLE_NAME, where={"bot_id": bot_id, "server_id": server_id})
