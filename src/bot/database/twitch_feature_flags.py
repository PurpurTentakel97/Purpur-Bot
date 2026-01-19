from typing import Any

from bot.core.types.programm_parts import PROGRAMM_PARTS
from bot.core.types.result import Result
from bot.database.types.feature_flags import TwitchFeatureFlagsDB

TABLE_NAME = "twitch_feature_flags"
FIELD_CAN_COMMANDS = "can_commands"
FIELD_CAN_ALIAS = "can_alias"


def insert_twitch_feature_flags(bot_id: int, channel_name: str) -> Result[int]:
    return PROGRAMM_PARTS.database.insert(table_name=TABLE_NAME, data={"bot_id": bot_id, "channel_name": channel_name})


def select_twitch_feature_flags_by_id(feature_flag_id: int) -> Result[TwitchFeatureFlagsDB]:
    return PROGRAMM_PARTS.database.select_one(
        table_name=TABLE_NAME, where={"id": feature_flag_id}, type_=TwitchFeatureFlagsDB
    )


def select_twitch_feature_flags_by_channel_name(bot_id: int, channel_name: str) -> Result[TwitchFeatureFlagsDB]:
    return PROGRAMM_PARTS.database.select_one(
        table_name=TABLE_NAME, where={"bot_id": bot_id, "channel_name": channel_name}, type_=TwitchFeatureFlagsDB
    )


def update_twitch_feature_flags_by_id(feature_flag_id: int, data: dict[str, Any]) -> Result[None]:
    return PROGRAMM_PARTS.database.update(table_name=TABLE_NAME, where={"id": feature_flag_id}, data=data)
