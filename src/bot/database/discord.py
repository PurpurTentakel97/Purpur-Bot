from bot.core.types.programm_parts import PROGRAMM_PARTS
from bot.core.types.result import Result
from bot.database.types.discord_server import DiscordServerDB

TABLE_NAME = "bot_discord_lookup"


def select_discord_servers_by_bot_id(bot_id: int) -> Result[list[DiscordServerDB]]:
    return PROGRAMM_PARTS.database.select_all(table_name=TABLE_NAME, where={"bot_id": bot_id}, type_=DiscordServerDB)


def insert_discord_server(bot_id: int, server_id: int, server_name: str) -> Result[int]:
    return PROGRAMM_PARTS.database.insert(
        table_name=TABLE_NAME, data={"bot_id": bot_id, "server_id": server_id, "server_name": server_name}
    )


def delete_discord_server(bot_id: int, server_id: int) -> Result[None]:
    return PROGRAMM_PARTS.database.delete(table_name=TABLE_NAME, where={"bot_id": bot_id, "server_id": server_id})
