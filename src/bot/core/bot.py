from bot.chat.on_demand import stop_all_discord_bots_from_bot
from bot.chat.on_demand import stop_all_twitch_bots_from_bot
from bot.core.helpers.string import name_for_db
from bot.core.helpers.string import strip_for_db
from bot.core.types.result import Result
from bot.database.bot import FIELD_ENABLED
from bot.database.bot import FIELD_NAME
from bot.database.bot import delete_bot as delete_bot_db
from bot.database.bot import insert_bot as insert_bot_db
from bot.database.bot import select_bot as select_bot_db
from bot.database.bot import select_bots_by_twitch_id as select_bots_by_twitch_id_db
from bot.database.bot import update_bot as update_bot_db
from bot.database.types.bot_config import BotConfigDB


def get_bot(bot_id: int) -> Result[BotConfigDB]:
    return select_bot_db(bot_id)


def get_bots_by_twitch_id(twitch_id: str) -> Result[list[BotConfigDB]]:
    return select_bots_by_twitch_id_db(strip_for_db(twitch_id))


def add_bot(twitch_id: str) -> Result[int]:
    return insert_bot_db(strip_for_db(twitch_id))


def update_bot(bot_id: int, name: str) -> Result[None]:
    return update_bot_db(bot_id, {FIELD_NAME: name_for_db(name)})


def update_bot_enabled_by_id(bot_id: int, enabled: bool) -> Result[None]:
    return update_bot_db(bot_id, {FIELD_ENABLED: enabled})


async def delete_bot(bot_id: int) -> Result[None]:
    await stop_all_twitch_bots_from_bot(bot_id)
    await stop_all_discord_bots_from_bot(bot_id)

    return delete_bot_db(bot_id)
