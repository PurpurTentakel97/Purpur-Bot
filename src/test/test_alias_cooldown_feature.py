from collections.abc import Generator
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from bot.chat.alias_dict import lookup_aliases
from bot.core.types.cooldown import CooldownsWrapper
from bot.core.types.permission_level import PermissionLevel
from bot.core.types.programm_parts import PROGRAMM_PARTS
from bot.core.types.result import Result
from bot.core.types.result import ResultState
from bot.database.types.alias_dict_entry import AliasDictEntry


@pytest.fixture(autouse=True)
def setup_programm_parts() -> Generator[None, None, None]:
    # Make sure we reset the GLOBAL PROGRAMM_PARTS.cooldowns
    with (
        patch("bot.core.app_context.APP_CONTEXT.twitch_live_message_cooldown_in_seconds.value", return_value=60),
        patch("bot.core.app_context.APP_CONTEXT.command_response_cooldown_in_seconds.value", return_value=60),
        patch("bot.core.app_context.APP_CONTEXT.alias_response_cooldown_in_seconds.value", return_value=60),
    ):
        PROGRAMM_PARTS.cooldowns = CooldownsWrapper()
        # Ensure data is empty
        PROGRAMM_PARTS.cooldowns.command_response_cooldown._data = {}  # type: ignore[reportPrivateUsage]
        PROGRAMM_PARTS.cooldowns.twitch_live_subscription._data = {}  # type: ignore[reportPrivateUsage]
        PROGRAMM_PARTS.cooldowns.alias_response_cooldown._data = {}  # type: ignore[reportPrivateUsage]
    yield


@pytest.fixture
def mock_twitch_message() -> MagicMock:
    message = MagicMock()
    message.text = "hello world"
    message.bot_id = 1
    message.sender_permission_level = PermissionLevel.USER
    message.sender_permission_level.is_permitted = MagicMock(return_value=False)
    message.has_twitch_message = True
    message.has_discord_message = False

    message.try_get_twitch_broadcaster_id = MagicMock(return_value="12345")
    message.try_get_discord_server_id = MagicMock(return_value=0)
    message.try_get_discord_channel_id = MagicMock(return_value=0)

    # Mock Chat
    message.sender_chat = MagicMock()
    message.sender_chat.is_twitch = True
    message.sender_chat.is_discord = False

    message.to_response_message = lambda x: x  # type: ignore[reportUnknownLambdaType, assignment]
    return message


@pytest.fixture
def mock_discord_message() -> MagicMock:
    message = MagicMock()
    message.text = "hello world"
    message.bot_id = 1
    message.sender_permission_level = PermissionLevel.USER
    message.sender_permission_level.is_permitted = MagicMock(return_value=False)
    message.has_twitch_message = False
    message.has_discord_message = True

    message.try_get_twitch_broadcaster_id = MagicMock(return_value="")
    message.try_get_discord_server_id = MagicMock(return_value=67890)
    message.try_get_discord_channel_id = MagicMock(return_value=54321)

    # Mock Chat
    message.sender_chat = MagicMock()
    message.sender_chat.is_twitch = False
    message.sender_chat.is_discord = True

    message.to_response_message = lambda x: x  # type: ignore[reportUnknownLambdaType, assignment]
    return message


@pytest.mark.asyncio
async def test_twitch_alias_cooldown(mock_twitch_message: MagicMock) -> None:
    # Setup
    bot_id = 1
    alias_entries = [
        AliasDictEntry(id=1, bot_id=bot_id, alias="hello", explanation="Hi there!", enabled=True),
    ]
    alias_result = Result(ResultState.SUCCESS, alias_entries)

    with patch("bot.core.alias_dict.select_dict_from_bot_db", return_value=alias_result):
        # First call - should succeed
        responses1 = lookup_aliases(mock_twitch_message)
        assert len(responses1) == 1
        assert responses1[0] == "hello: Hi there!"

        # Second call - should be in cooldown
        responses2 = lookup_aliases(mock_twitch_message)
        assert len(responses2) == 0


@pytest.mark.asyncio
async def test_discord_alias_cooldown(mock_discord_message: MagicMock) -> None:
    # Setup
    bot_id = 1
    alias_entries = [
        AliasDictEntry(id=1, bot_id=bot_id, alias="hello", explanation="Hi there!", enabled=True),
    ]
    alias_result = Result(ResultState.SUCCESS, alias_entries)

    with patch("bot.core.alias_dict.select_dict_from_bot_db", return_value=alias_result):
        # First call - should succeed
        responses1 = lookup_aliases(mock_discord_message)
        assert len(responses1) == 1
        assert responses1[0] == "hello: Hi there!"

        # Second call - should be in cooldown
        responses2 = lookup_aliases(mock_discord_message)
        assert len(responses2) == 0


@pytest.mark.asyncio
async def test_alias_cooldown_is_channel_specific(mock_twitch_message: MagicMock) -> None:
    # Setup
    bot_id = 1
    alias_entries = [
        AliasDictEntry(id=1, bot_id=bot_id, alias="hello", explanation="Hi there!", enabled=True),
    ]
    alias_result = Result(ResultState.SUCCESS, alias_entries)

    with patch("bot.core.alias_dict.select_dict_from_bot_db", return_value=alias_result):
        # First call from channel 1
        mock_twitch_message.try_get_twitch_broadcaster_id.return_value = "channel1"
        responses1 = lookup_aliases(mock_twitch_message)
        assert len(responses1) == 1
        assert responses1[0] == "hello: Hi there!"

        # Call from channel 2 - should also succeed
        mock_twitch_message.try_get_twitch_broadcaster_id.return_value = "channel2"
        responses2 = lookup_aliases(mock_twitch_message)
        assert len(responses2) == 1
        assert responses2[0] == "hello: Hi there!"

        # Call from channel 1 again - should be in cooldown
        mock_twitch_message.try_get_twitch_broadcaster_id.return_value = "channel1"
        responses3 = lookup_aliases(mock_twitch_message)
        assert len(responses3) == 0


@pytest.mark.asyncio
async def test_alias_cooldown_is_alias_specific(mock_twitch_message: MagicMock) -> None:
    # Setup
    bot_id = 1
    alias_entries = [
        AliasDictEntry(id=1, bot_id=bot_id, alias="hello", explanation="Hi!", enabled=True),
        AliasDictEntry(id=2, bot_id=bot_id, alias="bye", explanation="Goodbye!", enabled=True),
    ]
    alias_result = Result(ResultState.SUCCESS, alias_entries)

    with patch("bot.core.alias_dict.select_dict_from_bot_db", return_value=alias_result):
        # Message has both words
        mock_twitch_message.text = "hello bye"

        # First call - should get both
        responses1 = lookup_aliases(mock_twitch_message)
        assert len(responses1) == 2
        assert "hello: Hi!" in responses1
        assert "bye: Goodbye!" in responses1

        # Second call - both should be in cooldown
        responses2 = lookup_aliases(mock_twitch_message)
        assert len(responses2) == 0

        # Message with only one
        mock_twitch_message.text = "hello"
        responses3 = lookup_aliases(mock_twitch_message)
        assert len(responses3) == 0
