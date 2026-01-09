from bot.chat.on_demand import start_single_discord_bot
from bot.chat.on_demand import stop_single_discord_bot
from bot.core.types.result import Result
from bot.core.types.result import ResultState
from bot.database.discord import delete_discord_server as delete_discord_server_db
from bot.database.discord import insert_discord_server as insert_discord_server_db


def add_discord_bot(bot_id: int, discord_id: int, server_name: str) -> Result[int]:
    insert_result = insert_discord_server_db(bot_id, discord_id, server_name)

    if not insert_result.state.is_success():
        return insert_result

    add_result = start_single_discord_bot(bot_id, discord_id)

    if not add_result:
        delete_discord_server_db(bot_id, discord_id)
        return Result(ResultState.ERROR, None)

    return insert_result


async def delete_discord_bot(bot_id: int, discord_id: int) -> Result[None]:
    stop_result = await stop_single_discord_bot(bot_id, discord_id)

    if not stop_result:
        return Result(ResultState.ERROR, None)

    return delete_discord_server_db(bot_id, discord_id)
