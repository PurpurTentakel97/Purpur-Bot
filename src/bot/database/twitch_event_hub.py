from typing import Any

from bot.core.types.programm_parts import PROGRAMM_PARTS
from bot.core.types.result import Result
from bot.database.types.fields import FIELD_ENABLED
from bot.database.types.fields import FIELD_ID
from bot.database.types.fields import FIELD_TWITCH_BROADCASTER_ID
from bot.database.types.fields import TABLE_TWITCH_EVENT_HUB_NAME
from bot.database.types.twitch_event_hub import TwitchEventHubDB


def insert_twitch_event_hub(data: dict[str, Any]) -> Result[int]:
    return PROGRAMM_PARTS.database.insert(
        table_name=TABLE_TWITCH_EVENT_HUB_NAME,
        data=data,
    )


def select_all_enabled_twitch_hubs() -> Result[list[TwitchEventHubDB]]:
    return PROGRAMM_PARTS.database.select_all(
        table_name=TABLE_TWITCH_EVENT_HUB_NAME, where={FIELD_ENABLED: True}, type_=TwitchEventHubDB
    )


def select_twitch_event_hubs_by_server_id(server_id: int) -> Result[list[TwitchEventHubDB]]:
    from bot.database.types.fields import FIELD_DISCORD_SERVER_ID

    return PROGRAMM_PARTS.database.select_all(
        table_name=TABLE_TWITCH_EVENT_HUB_NAME,
        where={FIELD_DISCORD_SERVER_ID: server_id},
        type_=TwitchEventHubDB,
    )


def select_twitch_event_hub_by_id(id_: int) -> Result[TwitchEventHubDB]:
    return PROGRAMM_PARTS.database.select_one(
        table_name=TABLE_TWITCH_EVENT_HUB_NAME,
        where={FIELD_ID: id_},
        type_=TwitchEventHubDB,
    )


def select_twitch_event_hubs_by_broadcaster_id(broadcaster_id: str) -> Result[list[TwitchEventHubDB]]:
    return PROGRAMM_PARTS.database.select_all(
        table_name=TABLE_TWITCH_EVENT_HUB_NAME,
        where={FIELD_TWITCH_BROADCASTER_ID: broadcaster_id},
        type_=TwitchEventHubDB,
    )


def update_twitch_event_hub_by_id(id_: int, data: dict[str, Any]) -> Result[None]:
    return PROGRAMM_PARTS.database.update(
        table_name=TABLE_TWITCH_EVENT_HUB_NAME,
        where={FIELD_ID: id_},
        data=data,
    )


def delete_twitch_event_hub_by_id(id_: int) -> Result[None]:
    return PROGRAMM_PARTS.database.delete(
        table_name=TABLE_TWITCH_EVENT_HUB_NAME,
        where={FIELD_ID: id_},
    )
