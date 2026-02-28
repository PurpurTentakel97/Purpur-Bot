from unittest.mock import AsyncMock
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from bot.core.twitch_event_hub_management import send_twitch_event_hub_entry
from bot.core.types.cooldown import Cooldown
from bot.core.types.cooldown import CooldownsWrapper
from bot.core.types.cooldown import SubscriptionCooldownKey
from bot.core.types.result import Result
from bot.core.types.result import ResultState


@pytest.mark.asyncio
async def test_send_twitch_event_hub_entry_cooldown() -> None:
    # 1. Setup mocks
    broadcast_id = "12345"
    bot_id = 1
    server_id = 67890
    channel_id = 11111
    hub_id = 1

    mock_hub = MagicMock()
    mock_hub.id = hub_id
    mock_hub.bot_id = bot_id
    mock_hub.server_id = server_id
    mock_hub.channel_id = channel_id
    mock_hub.message = "Stream is live!"
    mock_hub.enabled = True

    mock_feature_flags = MagicMock()
    mock_feature_flags.can_twitch_live = True

    mock_message_light = MagicMock()
    mock_full_message = MagicMock()
    mock_message_light.advance.return_value = mock_full_message

    # Create a real Cooldown instance to test actual cooldown logic
    # Set it to a large enough value to ensure it stays in cooldown during the test
    cooldown_manager = Cooldown[SubscriptionCooldownKey](cooldown_in_seconds=60)
    cooldowns_wrapper = CooldownsWrapper()
    cooldowns_wrapper.twitch_live_subscription = cooldown_manager

    # Patching
    with (
        patch("bot.core.twitch_event_hub_management.PROGRAMM_PARTS") as mock_parts,
        patch("bot.core.twitch_event_hub_management.select_twitch_event_hubs_by_broadcaster_id_db") as mock_select_hubs,
        patch("bot.core.twitch_event_hub_management.select_discord_feature_flags_by_server_id") as mock_select_flags,
    ):
        # Configure mocks
        mock_parts.discord = AsyncMock()
        mock_parts.cooldowns = cooldowns_wrapper
        mock_select_hubs.return_value = Result(ResultState.SUCCESS, [mock_hub])
        mock_select_flags.return_value = Result(ResultState.SUCCESS, mock_feature_flags)

        # --- First Call: Should send message and add to cooldown ---
        await send_twitch_event_hub_entry(broadcast_id, mock_message_light)

        assert mock_parts.discord.send_twitch_live_message.call_count == 1
        mock_parts.discord.send_twitch_live_message.assert_called_with(mock_full_message)

        cooldown_key = SubscriptionCooldownKey(bot_id=bot_id, server_id=server_id, broadcast_id=broadcast_id)
        assert cooldown_manager.contains(cooldown_key)
        assert cooldown_manager.is_in_cooldown(cooldown_key)

        # Reset discord mock to track second call
        mock_parts.discord.send_twitch_live_message.reset_mock()

        # --- Second Call: Should be skipped due to cooldown ---
        await send_twitch_event_hub_entry(broadcast_id, mock_message_light)

        assert mock_parts.discord.send_twitch_live_message.call_count == 0

        # --- Third Call: After cooldown expires ---
        # Manually clear cooldown for testing the "after" state
        cooldown_manager.remove(cooldown_key)
        assert not cooldown_manager.is_in_cooldown(cooldown_key)

        await send_twitch_event_hub_entry(broadcast_id, mock_message_light)

        assert mock_parts.discord.send_twitch_live_message.call_count == 1
        assert cooldown_manager.is_in_cooldown(cooldown_key)
