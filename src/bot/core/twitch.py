from bot.chat.on_demand import start_single_twitch_bot
from bot.chat.on_demand import stop_single_twitch_bot
from bot.core.helpers.string import identifier_for_db
from bot.core.types.result import Result
from bot.core.types.result import ResultState
from bot.database.twitch import FIELD_CHANNEL_NAME
from bot.database.twitch import delete_twitch_channel as delete_twitch_channel_db
from bot.database.twitch import insert_twitch_channel as insert_twitch_channel_db
from bot.database.twitch import select_twitch_channel_by as select_twitch_channel_by_db
from bot.database.twitch import select_twitch_channels_by_bot_id as select_twitch_channels_db
from bot.database.twitch_feature_flags import insert_twitch_feature_flags as insert_twitch_feature_flags_db
from bot.database.types.twitch_channel import TwitchChannelDB


def _exists(channel: str) -> bool:
    return get_twitch_channel_by_name(channel).state.success


def get_twitch_channels_from_bot(bot_id: int) -> Result[list[TwitchChannelDB]]:
    return select_twitch_channels_db(bot_id)


def get_twitch_channel_by_name(channel_name: str) -> Result[TwitchChannelDB]:
    return select_twitch_channel_by_db({FIELD_CHANNEL_NAME: channel_name})


async def add_twitch_channel(bot_id: int, channel: str) -> Result[int]:
    channel_db = identifier_for_db(channel)

    if _exists(channel_db):
        return Result(ResultState.ALREADY_EXISTS, None)

    insert_result = insert_twitch_channel_db(bot_id, channel_db)

    if insert_result.state.fail:
        return insert_result

    feature_flag_result = insert_twitch_feature_flags_db(bot_id, channel_db)

    if feature_flag_result.state.fail:
        delete_twitch_channel_db(bot_id, channel_db)
        return Result(ResultState.ERROR, None)

    start_result = await start_single_twitch_bot(bot_id, channel_db)

    if not start_result:
        delete_twitch_channel_db(bot_id, channel_db)
        return Result(ResultState.ERROR, None)

    return insert_result


async def delete_twitch_channel(bot_id: int, channel: str) -> Result[None]:
    channel_db = identifier_for_db(channel)
    stop_result = await stop_single_twitch_bot(bot_id, channel_db)

    if not stop_result:
        return Result(ResultState.ERROR, None)

    return delete_twitch_channel_db(bot_id, channel_db)
