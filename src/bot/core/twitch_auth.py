from bot.core.types.result import Result
from bot.database.twitch_auth import delete_twitch_tokens as delete_twitch_tokens_db
from bot.database.twitch_auth import insert_twitch_tokens as insert_twitch_tokens_db
from bot.database.twitch_auth import select_twitch_tokens as select_twitch_tokens_db
from bot.database.twitch_auth import update_twitch_tokens as update_twitch_tokens_db
from bot.database.types.twitch_auth import TwitchAuthDB


def get_twitch_tokens(twitch_id: str) -> Result[TwitchAuthDB]:
    return select_twitch_tokens_db(twitch_id)


def store_or_update_twitch_tokens(
    twitch_id: str, access_token: str, refresh_token: str, expires_at: int
) -> Result[int]:
    insert_result = insert_twitch_tokens_db(twitch_id, access_token, refresh_token, expires_at)

    if insert_result.state.is_success():
        return insert_result

    update_result = update_twitch_tokens_db(twitch_id, access_token, refresh_token, expires_at)

    return Result(update_result.state, update_result.value)


def delete_twitch_tokens(twitch_id: str) -> Result[None]:
    return delete_twitch_tokens_db(twitch_id)
