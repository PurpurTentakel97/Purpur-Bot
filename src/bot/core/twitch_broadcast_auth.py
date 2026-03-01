from bot.core.helpers.string import strip_for_db
from bot.core.twitch_broadcast_client_factory import TWITCH_BROADCAST_CLIENT_FACTORY
from bot.core.types.result import Result
from bot.core.types.result import ResultState
from bot.database.twitch_broadcast_auth import delete_broadcast_tokens as delete_broadcast_tokens_db
from bot.database.twitch_broadcast_auth import insert_broadcast_tokens as insert_broadcast_tokens_db
from bot.database.twitch_broadcast_auth import select_broadcast_tokens as select_broadcast_tokens_db
from bot.database.twitch_broadcast_auth import update_broadcast_tokens as update_broadcast_tokens_db
from bot.database.types.twitch_broadcast_auth import TwitchBroadcastAuthDB


def get_broadcast_tokens(bot_id: int, channel_name: str) -> Result[TwitchBroadcastAuthDB]:
    return select_broadcast_tokens_db(bot_id, strip_for_db(channel_name))


def store_or_update_broadcast_tokens(
    bot_id: int, channel_name: str, twitch_user_id: str, access_token: str, refresh_token: str, expires_at: int
) -> Result[int]:
    channel_name_db = strip_for_db(channel_name)
    twitch_user_id_db = strip_for_db(twitch_user_id)
    access_token_db = strip_for_db(access_token)
    refresh_token_db = strip_for_db(refresh_token)

    insert_result = insert_broadcast_tokens_db(
        bot_id, channel_name_db, twitch_user_id_db, access_token_db, refresh_token_db, expires_at
    )

    if insert_result.state.success:
        return insert_result

    update_result = update_broadcast_tokens_db(
        bot_id, channel_name_db, twitch_user_id_db, access_token_db, refresh_token_db, expires_at
    )

    if update_result.state.fail and update_result.state != ResultState.NO_DATA:
        return update_result.cast_to(int)

    return Result(ResultState.SUCCESS, 0)


async def delete_broadcast_tokens(bot_id: int, channel_name: str) -> Result[None]:
    result = delete_broadcast_tokens_db(bot_id, strip_for_db(channel_name))
    if result.state.success:
        await TWITCH_BROADCAST_CLIENT_FACTORY.remove_client(bot_id, channel_name)
    return result
