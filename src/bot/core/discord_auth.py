from bot.core.helpers.string import strip_for_db
from bot.core.types.result import Result
from bot.core.types.result import ResultState
from bot.database.discord_auth import delete_discord_tokens as delete_discord_tokens_db
from bot.database.discord_auth import insert_discord_tokens as insert_discord_tokens_db
from bot.database.discord_auth import select_discord_tokens as select_discord_tokens_db
from bot.database.discord_auth import update_discord_tokens as update_discord_tokens_db
from bot.database.types.discord_auth import DiscordAuthDB


def get_discord_tokens(discord_id: int) -> Result[DiscordAuthDB]:
    return select_discord_tokens_db(discord_id)


def store_or_update_discord_tokens(
    discord_id: int, access_token: str, refresh_token: str, expires_at: int
) -> Result[int]:
    access_token_db = strip_for_db(access_token)
    refresh_token_db = strip_for_db(refresh_token)

    insert_result = insert_discord_tokens_db(discord_id, access_token_db, refresh_token_db, expires_at)

    if insert_result.state.success:
        return insert_result

    update_result = update_discord_tokens_db(discord_id, access_token_db, refresh_token_db, expires_at)

    if update_result.state.fail and update_result.state != ResultState.NO_DATA:
        return update_result.cast_to(int)

    return Result(ResultState.SUCCESS, discord_id)


def delete_discord_tokens(discord_id: int) -> Result[None]:
    return delete_discord_tokens_db(discord_id)
