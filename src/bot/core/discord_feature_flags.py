from bot.core.types.result import Result
from bot.database.discord_feature_flags import (
    select_discord_feature_flags_by_id as select_discord_feature_flags_by_id_db,
)
from bot.database.discord_feature_flags import (
    select_discord_feature_flags_by_server_id as select_discord_feature_flags_by_server_id_db,
)
from bot.database.discord_feature_flags import (
    update_discord_feature_flags_by_id as update_discord_feature_flags_by_id_db,
)
from bot.database.types.feature_flags import DiscordFeatureFlagsDB
from bot.database.types.fields import FIELD_CAN_ALIAS
from bot.database.types.fields import FIELD_CAN_COMMANDS
from bot.database.types.fields import FIELD_CAN_TWITCH_LIVE


def select_discord_feature_flags_by_id(feature_flag_id: int) -> Result[DiscordFeatureFlagsDB]:
    return select_discord_feature_flags_by_id_db(feature_flag_id)


def select_discord_feature_flags_by_server_id(bot_id: int, server_id: int) -> Result[DiscordFeatureFlagsDB]:
    return select_discord_feature_flags_by_server_id_db(bot_id, server_id)


def update_discord_feature_flags_by_id(
    feature_flag_id: int, can_commands: bool, can_alias: bool, can_twitch_live: bool
) -> Result[None]:
    return update_discord_feature_flags_by_id_db(
        feature_flag_id,
        {
            FIELD_CAN_COMMANDS: can_commands,
            FIELD_CAN_ALIAS: can_alias,
            FIELD_CAN_TWITCH_LIVE: can_twitch_live,
        },
    )
