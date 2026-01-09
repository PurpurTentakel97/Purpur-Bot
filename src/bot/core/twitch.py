from bot.chat.on_demand import start_single_twitch_bot
from bot.chat.on_demand import stop_single_twitch_bot
from bot.core.types.result import Result
from bot.core.types.result import ResultState
from bot.database.twitch import delete_twitch_channel as delete_twitch_channel_db
from bot.database.twitch import insert_twitch_channel as insert_twitch_channel_db


async def add_twitch_channel(bot_id: int, channel: str) -> Result[int]:
    insert_result = insert_twitch_channel_db(bot_id, channel)

    if not insert_result.state.is_success():
        return insert_result

    start_result = await start_single_twitch_bot(bot_id, channel)

    if not start_result:
        delete_twitch_channel_db(bot_id, channel)
        return Result(ResultState.ERROR, None)

    return insert_result


async def delete_twitch_channel(bot_id: int, channel: str) -> Result[None]:
    stop_result = await stop_single_twitch_bot(bot_id, channel)

    if not stop_result:
        return Result(ResultState.ERROR, None)

    return delete_twitch_channel_db(bot_id, channel)
