from bot.core.types.result import Result
from bot.database.twitch_feature_flags import (
    select_twitch_feature_flags_by_channel_name as select_twitch_feature_flags_by_channel_name_db,
)
from bot.database.twitch_feature_flags import select_twitch_feature_flags_by_id as select_twitch_feature_flags_by_id_db
from bot.database.twitch_feature_flags import update_twitch_feature_flags_by_id as update_twitch_feature_flags_by_id_db
from bot.database.types.feature_flags import TwitchFeatureFlagsDB
from bot.database.types.fields import FIELD_CAN_ALIAS
from bot.database.types.fields import FIELD_CAN_BROADCAST
from bot.database.types.fields import FIELD_CAN_COMMANDS


def select_twitch_feature_flags_by_id(feature_flag_id: int) -> Result[TwitchFeatureFlagsDB]:
    return select_twitch_feature_flags_by_id_db(feature_flag_id)


def select_twitch_feature_flags_by_channel_name(bot_id: int, channel_name: str) -> Result[TwitchFeatureFlagsDB]:
    return select_twitch_feature_flags_by_channel_name_db(bot_id, channel_name)


def update_twitch_feature_flags_by_id(
    feature_flag_id: int, can_commands: bool, can_alias: bool, can_broadcast: bool
) -> Result[None]:
    return update_twitch_feature_flags_by_id_db(
        feature_flag_id,
        {
            FIELD_CAN_COMMANDS: can_commands,
            FIELD_CAN_ALIAS: can_alias,
            FIELD_CAN_BROADCAST: can_broadcast,
        },
    )
