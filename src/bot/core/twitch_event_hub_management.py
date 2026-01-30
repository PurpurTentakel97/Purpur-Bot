from bot.core.types.programm_parts import PROGRAMM_PARTS
from bot.core.types.result import Result, ResultState
from bot.core.types.twitch_online_message import TwitchOnlineMessage
from bot.database.twitch_event_hub import delete_twitch_event_hub_by_id as delete_twitch_event_hub_by_id_db
from bot.database.twitch_event_hub import insert_twitch_event_hub as insert_twitch_event_hub_db
from bot.database.twitch_event_hub import select_twitch_event_hub_by_id as select_twitch_event_hub_by_id_db
from bot.database.types.fields import FIELD_BOT_ID
from bot.database.types.fields import FIELD_DISCORD_CHANNEL_ID
from bot.database.types.fields import FIELD_DISCORD_SERVER_ID
from bot.database.types.fields import FIELD_TWITCH_BROADCASTER_ID
from bot.database.types.fields import FIELD_TWITCH_LIVE_MESSAGE


async def add_twitch_event_hub_entry(
    bot_id: int, server_id: int, channel_id: int, broadcaster_id: str, message: str
) -> Result[int]:
    data = {
        FIELD_BOT_ID: bot_id,
        FIELD_DISCORD_SERVER_ID: server_id,
        FIELD_DISCORD_CHANNEL_ID: channel_id,
        FIELD_TWITCH_BROADCASTER_ID: broadcaster_id,
        FIELD_TWITCH_LIVE_MESSAGE: message,
    }

    result = insert_twitch_event_hub_db(data)

    if result.state.success and PROGRAMM_PARTS.event_hub:
        await PROGRAMM_PARTS.event_hub.subscribe(broadcaster_id)

    return result


async def send_test_twitch_event_hub_entry(id_: int) -> Result[None]:
    if not PROGRAMM_PARTS.discord:
        return Result(ResultState.BOT_DISABLED, None)

    hub_entry = select_twitch_event_hub_by_id_db(id_)
    if hub_entry.state.fail or hub_entry.value is None:
        return hub_entry.cast_to(type(None))

    message = TwitchOnlineMessage(
        id=hub_entry.value.id,
        discord_server_id=hub_entry.value.server_id,
        discord_channel_id=hub_entry.value.channel_id,
        message=hub_entry.value.message,
    )

    await PROGRAMM_PARTS.discord.send_twitch_live_message(message)

    return Result(ResultState.SUCCESS, None)


async def delete_twitch_event_hub_entry(id_: int) -> Result[None]:
    hub_entry = select_twitch_event_hub_by_id_db(id_)
    if hub_entry.state.fail or hub_entry.value is None:
        return hub_entry.cast_to(type(None))

    result = delete_twitch_event_hub_by_id_db(id_)

    if result.state.success and PROGRAMM_PARTS.event_hub:
        await PROGRAMM_PARTS.event_hub.unsubscribe(hub_entry.value.broadcaster_id)

    return result
