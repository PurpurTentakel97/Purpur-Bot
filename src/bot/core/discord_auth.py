from bot.core.types.result import Result
from bot.database.discord_auth import delete_discord_tokens as delete_discord_tokens_db
from bot.database.discord_auth import insert_discord_tokens as insert_discord_tokens_db
from bot.database.discord_auth import select_discord_tokens as select_discord_tokens_db
from bot.database.discord_auth import update_discord_tokens as update_discord_tokens_db
from bot.database.types.discord_auth import DiscordAuthDB


def get_discord_auth(discord_id: int) -> Result[DiscordAuthDB]:
    return select_discord_tokens_db(discord_id)


def store_or_update_discord_tokens(
    discord_id: int, access_token: str, refresh_token: str, expires_at: int
) -> Result[int]:
    insert_result = insert_discord_tokens_db(discord_id, access_token, refresh_token, expires_at)

    if insert_result.state.is_success():
        return insert_result

    update_result = update_discord_tokens_db(discord_id, access_token, refresh_token, expires_at)

    return Result(update_result.state, update_result.value)


def delete_discord_tokens(discord_id: int) -> Result[None]:
    return delete_discord_tokens_db(discord_id)
