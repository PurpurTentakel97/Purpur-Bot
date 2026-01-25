from typing import Any

from bot.core.types.programm_parts import PROGRAMM_PARTS
from bot.core.types.result import Result
from bot.database.types.discord_server import DiscordServerDB

TABLE_NAME = "bot_discord_lookup"
FIELD_SERVER_ID = "server_id"
FIELD_ENABLED = "enabled"
FIELD_BOT_ID = "bot_id"


def select_discord_servers_by(where: dict[str, Any]) -> Result[list[DiscordServerDB]]:
    return PROGRAMM_PARTS.database.select_all(table_name=TABLE_NAME, where=where, type_=DiscordServerDB)


def select_discord_by(where: dict[str, Any]) -> Result[DiscordServerDB]:
    return PROGRAMM_PARTS.database.select_one(table_name=TABLE_NAME, where=where, type_=DiscordServerDB)


def insert_discord_server(bot_id: int, server_id: int, server_name: str) -> Result[int]:
    return PROGRAMM_PARTS.database.insert(
        table_name=TABLE_NAME, data={"bot_id": bot_id, "server_id": server_id, "server_name": server_name}
    )


def update_discord_server_by_id(id_: int, data: dict[str, Any]) -> Result[None]:
    return PROGRAMM_PARTS.database.update(table_name=TABLE_NAME, where={"id": id_}, data=data)


def delete_discord_server(bot_id: int, server_id: int) -> Result[None]:
    return PROGRAMM_PARTS.database.delete(table_name=TABLE_NAME, where={"bot_id": bot_id, "server_id": server_id})
