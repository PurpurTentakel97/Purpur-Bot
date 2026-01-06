from typing import Optional

from bot.chat.on_demand import start_single_discord_bot
from bot.chat.on_demand import start_single_twitch_bot
from bot.chat.on_demand import stop_single_discord_bot
from bot.chat.on_demand import stop_single_twitch_bot
from bot.database.types import BotConfig
from bot.database.types import DiscordServer
from bot.database.types import TwitchChannel
from bot.types.programm_parts import PROGRAMM_PARTS


# bot
def get_bot_by_id(bot_id: int) -> Optional[BotConfig]:
    return PROGRAMM_PARTS.database.find_one(table_name="bot_config", where={"id": bot_id}, type_=BotConfig)


def get_bots_by_twitch_id(twitch_user_id: str) -> list[BotConfig]:
    return PROGRAMM_PARTS.database.find_all(
        table_name="bot_config", where={"twitch_user_id": twitch_user_id}, type_=BotConfig
    )


def create_new_bot(twitch_user_id: str) -> Optional[int]:
    return PROGRAMM_PARTS.database.save_with_returned_id(
        table_name="bot_config", data={"twitch_user_id": twitch_user_id}
    )


def update_bot(bot_id: int, twitch_id: str, new_name: str) -> bool:
    return PROGRAMM_PARTS.database.update(
        table_name="bot_config", where={"id": bot_id, "twitch_user_id": twitch_id}, data={"name": new_name}
    )


async def delete_bot_by_id(id_: int, twitch_user_id: str) -> bool:
    # Stop all twitch channels for this bot
    twitch_channels = get_twitch_channels_by_bot_id(id_)
    for channel in twitch_channels:
        await stop_single_twitch_bot(id_, channel.channel_name)

    # Stop all discord servers for this bot
    discord_servers = get_discord_servers_by_bot_id(id_)
    for server in discord_servers:
        await stop_single_discord_bot(id_, server.server_id)

    return PROGRAMM_PARTS.database.delete(table_name="bot_config", where={"id": id_, "twitch_user_id": twitch_user_id})


# twitch
def get_twitch_channels_by_bot_id(bot_id: int) -> list[TwitchChannel]:
    return PROGRAMM_PARTS.database.find_all(table_name="bot_twitch_lookup", where={"id": bot_id}, type_=TwitchChannel)


async def add_twitch_channel_to_bot(bot_id: int, twitch_channel: str) -> bool:
    result = PROGRAMM_PARTS.database.find_one(
        table_name="bot_twitch_lookup", where={"bot_id": bot_id, "channel_name": twitch_channel}, type_=TwitchChannel
    )

    if result is not None:
        return False

    result = PROGRAMM_PARTS.database.save(
        table_name="bot_twitch_lookup", data={"bot_id": bot_id, "channel_name": twitch_channel}
    )

    if not result:
        return False

    result = await start_single_twitch_bot(bot_id, twitch_channel)

    return result


async def delete_twitch_channel_from_bot(bot_id: int, twitch_channel: str) -> bool:
    result = PROGRAMM_PARTS.database.delete(
        table_name="bot_twitch_lookup", where={"bot_id": bot_id, "channel_name": twitch_channel}
    )

    if not result:
        return False

    result = await stop_single_twitch_bot(bot_id, twitch_channel)

    return result


# discord
def get_discord_servers_by_bot_id(bot_id: int) -> list[DiscordServer]:
    return PROGRAMM_PARTS.database.find_all(
        table_name="bot_discord_lookup", where={"bot_id": bot_id}, type_=DiscordServer
    )


async def add_discord_server_to_bot(bot_id: int, server_id: int, server_name: str) -> bool:
    result = PROGRAMM_PARTS.database.find_one(
        table_name="bot_discord_lookup", where={"bot_id": bot_id, "server_id": server_id}, type_=DiscordServer
    )

    if result is not None:
        return False

    result = PROGRAMM_PARTS.database.save(
        table_name="bot_discord_lookup", data={"bot_id": bot_id, "server_id": server_id, "server_name": server_name}
    )

    if not result:
        return False

    result = await start_single_discord_bot(bot_id, server_id)

    return result


async def delete_discord_server_from_bot(bot_id: int, server_id: int) -> bool:
    result = PROGRAMM_PARTS.database.delete(
        table_name="bot_discord_lookup", where={"bot_id": bot_id, "server_id": server_id}
    )

    if not result:
        return False

    result = await stop_single_discord_bot(bot_id, server_id)

    return result
