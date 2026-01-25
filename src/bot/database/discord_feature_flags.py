from typing import Any

from bot.core.types.programm_parts import PROGRAMM_PARTS
from bot.core.types.result import Result
from bot.database.types.feature_flags import DiscordFeatureFlagsDB
from bot.database.types.fields import FIELD_BOT_ID
from bot.database.types.fields import FIELD_DISCORD_SERVER_ID
from bot.database.types.fields import FIELD_ID
from bot.database.types.fields import TABLE_DISCORD_FEATURE_FLAGS_NAME


def insert_discord_feature_flags(bot_id: int, server_id: int) -> Result[int]:
    return PROGRAMM_PARTS.database.insert(
        table_name=TABLE_DISCORD_FEATURE_FLAGS_NAME, data={FIELD_BOT_ID: bot_id, FIELD_DISCORD_SERVER_ID: server_id}
    )


def select_discord_feature_flags_by_id(feature_flag_id: int) -> Result[DiscordFeatureFlagsDB]:
    return PROGRAMM_PARTS.database.select_one(
        table_name=TABLE_DISCORD_FEATURE_FLAGS_NAME, where={FIELD_ID: feature_flag_id}, type_=DiscordFeatureFlagsDB
    )


def select_discord_feature_flags_by_server_id(bot_id: int, server_id: int) -> Result[DiscordFeatureFlagsDB]:
    return PROGRAMM_PARTS.database.select_one(
        table_name=TABLE_DISCORD_FEATURE_FLAGS_NAME,
        where={FIELD_BOT_ID: bot_id, FIELD_DISCORD_SERVER_ID: server_id},
        type_=DiscordFeatureFlagsDB,
    )


def update_discord_feature_flags_by_id(feature_flag_id: int, data: dict[str, Any]) -> Result[None]:
    return PROGRAMM_PARTS.database.update(
        table_name=TABLE_DISCORD_FEATURE_FLAGS_NAME, where={FIELD_ID: feature_flag_id}, data=data
    )
