from twitchAPI.helper import first

from bot.core.types.programm_parts import PROGRAMM_PARTS
from bot.core.types.result import Result
from bot.core.types.result import ResultState
from bot.core.types.twitch_online_message import TwitchOnlineMessage
from bot.database.twitch_event_hub import delete_twitch_event_hub_by_id as delete_twitch_event_hub_by_id_db
from bot.database.twitch_event_hub import insert_twitch_event_hub as insert_twitch_event_hub_db
from bot.database.twitch_event_hub import select_twitch_event_hub_by_id as select_twitch_event_hub_by_id_db
from bot.database.twitch_event_hub import (
    select_twitch_event_hubs_by_broadcaster_id as select_twitch_event_hubs_by_broadcaster_id_db,
)
from bot.database.twitch_event_hub import update_twitch_event_hub_by_id as update_twitch_event_hub_by_id_db
from bot.database.types.fields import FIELD_BOT_ID
from bot.database.types.fields import FIELD_DISCORD_CHANNEL_ID
from bot.database.types.fields import FIELD_DISCORD_SERVER_ID
from bot.database.types.fields import FIELD_ENABLED
from bot.database.types.fields import FIELD_TWITCH_BROADCASTER_ID
from bot.database.types.fields import FIELD_TWITCH_LIVE_MESSAGE


async def _subscribe(broadcaster_id: str) -> None:
    if not PROGRAMM_PARTS.event_hub:
        return None

    return await PROGRAMM_PARTS.event_hub.subscribe(broadcaster_id)


async def _unsubscribe(broadcaster_id: str) -> None:
    if not PROGRAMM_PARTS.event_hub:
        return None

    hubs_by_broadcaster_id = select_twitch_event_hubs_by_broadcaster_id_db(broadcaster_id)
    if hubs_by_broadcaster_id.state.fail or hubs_by_broadcaster_id.value is None:
        return None

    if len(hubs_by_broadcaster_id.value) == 0:
        return await PROGRAMM_PARTS.event_hub.unsubscribe(broadcaster_id)

    return None


async def add_twitch_event_hub_entry(
    bot_id: int,
    server_id: int,
    channel_id: int,
    broadcaster_id: str,
    message: str,
) -> Result[int]:
    data = {
        FIELD_BOT_ID: bot_id,
        FIELD_DISCORD_SERVER_ID: server_id,
        FIELD_DISCORD_CHANNEL_ID: channel_id,
        FIELD_TWITCH_BROADCASTER_ID: broadcaster_id,
        FIELD_TWITCH_LIVE_MESSAGE: message,
    }

    result = insert_twitch_event_hub_db(data)

    await _subscribe(broadcaster_id)

    return result


async def send_test_twitch_event_hub_entry(id_: int) -> Result[None]:
    if PROGRAMM_PARTS.discord is None:
        return Result(ResultState.BOT_DISABLED, None)

    if PROGRAMM_PARTS.twitch is None:
        return Result(ResultState.BOT_DISABLED, None)

    hub_entry = select_twitch_event_hub_by_id_db(id_)
    if hub_entry.state.fail or hub_entry.value is None:
        return hub_entry.cast_to(type(None))

    channel_name = await first(PROGRAMM_PARTS.twitch.client.get_users(user_ids=[hub_entry.value.broadcaster_id]))
    if not channel_name:
        return Result(ResultState.ERROR, None)

    message = TwitchOnlineMessage(
        id=hub_entry.value.id,
        discord_server_id=hub_entry.value.server_id,
        discord_channel_id=hub_entry.value.channel_id,
        message=hub_entry.value.message,
        broadcaster_name=channel_name.display_name,
        stream_title="Stream Title | Product Placement (Kappa) | Obviously no real stream title",
        category_name="Category Name",
        channel_url=f"https://twitch.tv/{channel_name.display_name.lower()}",
    )

    await PROGRAMM_PARTS.discord.send_twitch_live_message(message)

    return Result(ResultState.SUCCESS, None)


async def update_twitch_event_hub(id_: int, message: str, enabled: bool) -> Result[None]:
    result = update_twitch_event_hub_by_id_db(id_, {FIELD_TWITCH_LIVE_MESSAGE: message, FIELD_ENABLED: enabled})

    if result.state.fail:
        return result

    hub_entry = select_twitch_event_hub_by_id_db(id_)
    if hub_entry.state.fail or hub_entry.value is None:
        return hub_entry.cast_to(type(None))

    if enabled:
        await _subscribe(hub_entry.value.broadcaster_id)
    else:
        await _unsubscribe(hub_entry.value.broadcaster_id)

    return result


async def delete_twitch_event_hub_entry(id_: int) -> Result[None]:
    hub_entry = select_twitch_event_hub_by_id_db(id_)
    if hub_entry.state.fail or hub_entry.value is None:
        return hub_entry.cast_to(type(None))

    delete_result = delete_twitch_event_hub_by_id_db(id_)

    if not delete_result.state.success:
        return delete_result

    await _unsubscribe(hub_entry.value.broadcaster_id)

    return delete_result
