from datetime import UTC
from datetime import datetime
from datetime import timedelta
from unittest.mock import AsyncMock
from unittest.mock import patch

import pytest

from bot.core.twitch_event_hub_management import CooldownKey
from bot.core.twitch_event_hub_management import send_twitch_event_hub_entry
from bot.core.twitch_event_hub_management import twitch_live_message_cooldown_table
from bot.core.types.result import Result
from bot.core.types.result import ResultState
from bot.core.types.twitch_online_message import TwitchOnlineMessageLight
from bot.database.types.feature_flags import DiscordFeatureFlagsDB
from bot.database.types.twitch_event_hub import TwitchEventHubDB


@pytest.fixture(autouse=True)
def clear_cooldown_table() -> None:
    twitch_live_message_cooldown_table.clear()


@pytest.mark.asyncio
async def test_send_twitch_event_hub_entry_cooldown_logic() -> None:
    broadcast_id = "12345"
    bot_id = 1
    server_id = 100
    channel_id = 200

    hub_entry = TwitchEventHubDB(
        id=1,
        bot_id=bot_id,
        broadcaster_id=broadcast_id,
        message="Stream is live!",
        server_id=server_id,
        channel_id=channel_id,
        enabled=True,
    )

    feature_flags = DiscordFeatureFlagsDB(
        id=1,
        bot_id=bot_id,
        server_id=server_id,
        can_commands=True,
        can_alias=True,
        can_broadcast=True,
        can_twitch_live=True,
    )

    message_light = TwitchOnlineMessageLight(
        broadcaster_id=broadcast_id,
        broadcaster_name="TestBroadcaster",
        channel_url="https://twitch.tv/test",
        stream_title="Test Stream",
        category_name="Test Category",
    )

    with (
        patch("bot.core.twitch_event_hub_management.PROGRAMM_PARTS") as mock_parts,
        patch("bot.core.twitch_event_hub_management.select_twitch_event_hubs_by_broadcaster_id_db") as mock_select_hubs,
        patch("bot.core.twitch_event_hub_management.select_discord_feature_flags_by_server_id") as mock_select_flags,
        patch("bot.core.twitch_event_hub_management.APP_CONTEXT") as mock_app_context,
    ):
        mock_parts.discord = AsyncMock()
        mock_select_hubs.return_value = Result(ResultState.SUCCESS, [hub_entry])
        mock_select_flags.return_value = Result(ResultState.SUCCESS, feature_flags)
        mock_app_context.twitch_live_message_cooldown_in_minutes.value.return_value = 10

        # 1. First call: No cooldown present
        await send_twitch_event_hub_entry(broadcast_id, message_light)

        assert mock_parts.discord.send_twitch_live_message.call_count == 1
        cooldown_key = CooldownKey(bot_id=bot_id, server_id=server_id, broadcast_id=broadcast_id)
        assert cooldown_key in twitch_live_message_cooldown_table

        # 2. Second call: Cooldown is active
        mock_parts.discord.send_twitch_live_message.reset_mock()
        await send_twitch_event_hub_entry(broadcast_id, message_light)

        assert mock_parts.discord.send_twitch_live_message.call_count == 0

        # 3. Third call: Cooldown passed
        mock_parts.discord.send_twitch_live_message.reset_mock()
        # Manually set the cooldown to be in the past (11 minutes ago, with a 10-minute cooldown)
        old_time = datetime.now(UTC) - timedelta(minutes=11)
        twitch_live_message_cooldown_table[cooldown_key] = old_time

        await send_twitch_event_hub_entry(broadcast_id, message_light)

        assert mock_parts.discord.send_twitch_live_message.call_count == 1
        assert twitch_live_message_cooldown_table[cooldown_key] > old_time


@pytest.mark.asyncio
async def test_send_twitch_event_hub_entry_cooldown_per_key() -> None:
    broadcast_id = "12345"
    bot_id = 1
    server_id_1 = 100
    server_id_2 = 101

    hub_entry_1 = TwitchEventHubDB(
        id=1,
        bot_id=bot_id,
        broadcaster_id=broadcast_id,
        message="Live 1",
        server_id=server_id_1,
        channel_id=200,
        enabled=True,
    )
    hub_entry_2 = TwitchEventHubDB(
        id=2,
        bot_id=bot_id,
        broadcaster_id=broadcast_id,
        message="Live 2",
        server_id=server_id_2,
        channel_id=201,
        enabled=True,
    )

    message_light = TwitchOnlineMessageLight(
        broadcaster_id=broadcast_id,
        broadcaster_name="Test",
        channel_url="url",
        stream_title="title",
        category_name="cat",
    )

    with (
        patch("bot.core.twitch_event_hub_management.PROGRAMM_PARTS") as mock_parts,
        patch("bot.core.twitch_event_hub_management.select_twitch_event_hubs_by_broadcaster_id_db") as mock_select_hubs,
        patch("bot.core.twitch_event_hub_management.select_discord_feature_flags_by_server_id") as mock_select_flags,
        patch("bot.core.twitch_event_hub_management.APP_CONTEXT") as mock_app_context,
    ):
        mock_parts.discord = AsyncMock()
        mock_select_hubs.return_value = Result(ResultState.SUCCESS, [hub_entry_1, hub_entry_2])

        # Return flags based on server_id
        def get_flags(bid: int, sid: int) -> Result[DiscordFeatureFlagsDB]:
            return Result(
                ResultState.SUCCESS,
                DiscordFeatureFlagsDB(
                    id=sid,
                    bot_id=bid,
                    server_id=sid,
                    can_commands=True,
                    can_alias=True,
                    can_broadcast=True,
                    can_twitch_live=True,
                ),
            )

        mock_select_flags.side_effect = get_flags
        mock_app_context.twitch_live_message_cooldown_in_minutes.value.return_value = 10

        # Call for both hubs
        await send_twitch_event_hub_entry(broadcast_id, message_light)

        assert mock_parts.discord.send_twitch_live_message.call_count == 2
        assert CooldownKey(bot_id, server_id_1, broadcast_id) in twitch_live_message_cooldown_table
        assert CooldownKey(bot_id, server_id_2, broadcast_id) in twitch_live_message_cooldown_table

        # Second call: Both on cooldown
        mock_parts.discord.send_twitch_live_message.reset_mock()
        await send_twitch_event_hub_entry(broadcast_id, message_light)
        assert mock_parts.discord.send_twitch_live_message.call_count == 0
