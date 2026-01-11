from bot.core.helpers.string import strip_for_db
from bot.core.types.result import Result
from bot.core.types.result import ResultState
from bot.database.twitch_auth import delete_twitch_tokens as delete_twitch_tokens_db
from bot.database.twitch_auth import insert_twitch_tokens as insert_twitch_tokens_db
from bot.database.twitch_auth import select_twitch_tokens as select_twitch_tokens_db
from bot.database.twitch_auth import update_twitch_tokens as update_twitch_tokens_db
from bot.database.types.twitch_auth import TwitchAuthDB


def get_twitch_tokens(twitch_id: str) -> Result[TwitchAuthDB]:
    return select_twitch_tokens_db(strip_for_db(twitch_id))


def store_or_update_twitch_tokens(
    twitch_id: str, access_token: str, refresh_token: str, expires_at: int
) -> Result[int]:
    twitch_id_db = strip_for_db(twitch_id)
    access_token_db = strip_for_db(access_token)
    refresh_token_db = strip_for_db(refresh_token)

    insert_result = insert_twitch_tokens_db(twitch_id_db, access_token_db, refresh_token_db, expires_at)

    if insert_result.state.success:
        return insert_result

    update_result = update_twitch_tokens_db(twitch_id_db, access_token_db, refresh_token_db, expires_at)

    if update_result.state.fail and update_result.state != ResultState.NO_DATA:
        return update_result.cast_to(int)

    return Result(ResultState.SUCCESS, 0)


def delete_twitch_tokens(twitch_id: str) -> Result[None]:
    return delete_twitch_tokens_db(strip_for_db(twitch_id))
