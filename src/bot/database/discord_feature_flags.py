from typing import Any

from bot.core.types.programm_parts import PROGRAMM_PARTS
from bot.core.types.result import Result
from bot.database.types.feature_flags import DiscordFeatureFlagsDB

TABLE_NAME = "discord_feature_flags"
FIELD_CAN_COMMANDS = "can_commands"
FIELD_CAN_ALIAS = "can_alias"


def insert_discord_feature_flags(bot_id: int, server_id: str) -> Result[int]:
    return PROGRAMM_PARTS.database.insert(table_name=TABLE_NAME, data={"bot_id": bot_id, "server_id": server_id})


def select_discord_feature_flags_by_id(feature_flag_id: int) -> Result[DiscordFeatureFlagsDB]:
    return PROGRAMM_PARTS.database.select_one(
        table_name=TABLE_NAME, where={"id": feature_flag_id}, type_=DiscordFeatureFlagsDB
    )


def select_discord_feature_flags_by_server_id(bot_id: int, server_id: str) -> Result[DiscordFeatureFlagsDB]:
    return PROGRAMM_PARTS.database.select_one(
        table_name=TABLE_NAME, where={"bot_id": bot_id, "server_id": server_id}, type_=DiscordFeatureFlagsDB
    )


def update_discord_feature_flags_by_id(feature_flag_id: int, data: dict[str, Any]) -> Result[None]:
    return PROGRAMM_PARTS.database.update(table_name=TABLE_NAME, where={"id": feature_flag_id}, data=data)
