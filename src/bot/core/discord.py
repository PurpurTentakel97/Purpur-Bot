from bot.chat.on_demand import start_single_discord_bot
from bot.chat.on_demand import stop_single_discord_bot
from bot.core.helpers.string import name_for_db
from bot.core.types.result import Result
from bot.core.types.result import ResultState
from bot.database.discord import FIELD_SERVER_ID
from bot.database.discord import delete_discord_server as delete_discord_server_db
from bot.database.discord import insert_discord_server as insert_discord_server_db
from bot.database.discord import select_discord_by as select_discord_by_db
from bot.database.discord import select_discord_servers_by_bot_id as select_discord_servers_by_bot_id_db
from bot.database.discord_feature_flags import insert_discord_feature_flags as insert_discord_feature_flags_db
from bot.database.types.discord_server import DiscordServerDB


def _exists(server_id: int) -> bool:
    return get_discord_by_server_id(server_id).state.success


def get_discord_servers_by_bot_id(bot_id: int) -> Result[list[DiscordServerDB]]:
    return select_discord_servers_by_bot_id_db(bot_id)


def get_discord_by_server_id(server_id: int) -> Result[DiscordServerDB]:
    return select_discord_by_db({FIELD_SERVER_ID: server_id})


def add_discord_bot(bot_id: int, discord_id: int, server_name: str) -> Result[int]:
    if _exists(discord_id):
        return Result(ResultState.ALREADY_EXISTS, None)

    insert_result = insert_discord_server_db(bot_id, discord_id, name_for_db(server_name))

    if insert_result.state.fail:
        return insert_result

    feature_flag_result = insert_discord_feature_flags_db(bot_id, str(discord_id))

    if feature_flag_result.state.fail:
        delete_discord_server_db(bot_id, discord_id)
        return Result(ResultState.ERROR, None)

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
