from collections.abc import Generator
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
from twitchAPI.chat import ChatMessage as TwitchChatMessage

from bot.chat.handle_commands import handle_command
from bot.chat.types.message import ChatMessage
from bot.chat.types.user_ref import TwitchUserRef
from bot.core.types.cooldown import CooldownsWrapper
from bot.core.types.permission_level import PermissionLevel
from bot.core.types.programm_parts import PROGRAMM_PARTS
from bot.core.types.result import Result
from bot.core.types.result import ResultState
from bot.database.types.base_command import BasicCommandDB
from bot.database.types.feature_flags import FeatureFlagsDB


@pytest.fixture(autouse=True)
def setup_programm_parts() -> Generator[None, None, None]:
    # Make sure we reset the GLOBAL PROGRAMM_PARTS.cooldowns
    with (
        patch("bot.core.app_context.APP_CONTEXT.twitch_live_message_cooldown_in_seconds.value", return_value=60),
        patch("bot.core.app_context.APP_CONTEXT.command_response_cooldown_in_seconds.value", return_value=60),
    ):
        PROGRAMM_PARTS.cooldowns = CooldownsWrapper()
        # Ensure data is empty
        PROGRAMM_PARTS.cooldowns.command_response_cooldown._data = {}  # type: ignore[reportPrivateUsage]
        PROGRAMM_PARTS.cooldowns.twitch_live_subscription._data = {}  # type: ignore[reportPrivateUsage]
    yield


@pytest.fixture
def mock_feature_flags() -> FeatureFlagsDB:
    return FeatureFlagsDB(
        id=1,
        bot_id=1,
        can_commands=True,
        can_alias=True,
        can_broadcast=True,
        can_twitch_live=True,
        can_quote=True,
    )


@pytest.fixture
def mock_twitch_message() -> MagicMock:
    message = MagicMock()
    message.text = "!hello"
    message.bot_id = 1
    message.sender_permission_level = PermissionLevel.USER
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
    message.text = "!hello"
    message.bot_id = 1
    message.sender_permission_level = PermissionLevel.USER
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
async def test_twitch_command_cooldown(mock_twitch_message: MagicMock, mock_feature_flags: FeatureFlagsDB) -> None:
    # Setup
    command_name = "hello"
    bot_id = 1
    command_result = Result(
        ResultState.SUCCESS,
        BasicCommandDB(
            id=1,
            bot_id=bot_id,
            command=command_name,
            message="Hi there!",
            enabled=True,
            permission_level=PermissionLevel.USER,
        ),
    )

    with patch("bot.chat.handle_commands.get_command_core", return_value=command_result):
        # First call - should succeed
        response1 = await handle_command(mock_twitch_message, mock_feature_flags)
        assert response1 == "Hi there!"

        # Second call - should be in cooldown
        response2 = await handle_command(mock_twitch_message, mock_feature_flags)
        assert response2 is None


@pytest.mark.asyncio
async def test_discord_command_cooldown(mock_discord_message: MagicMock, mock_feature_flags: FeatureFlagsDB) -> None:
    # Setup
    command_name = "hello"
    bot_id = 1
    command_result = Result(
        ResultState.SUCCESS,
        BasicCommandDB(
            id=1,
            bot_id=bot_id,
            command=command_name,
            message="Hi there!",
            enabled=True,
            permission_level=PermissionLevel.USER,
        ),
    )

    # We need to mock DiscordMessage class for isinstance check
    with patch("bot.chat.handle_commands.get_command_core", return_value=command_result):
        # First call - should succeed
        response1 = await handle_command(mock_discord_message, mock_feature_flags)
        assert response1 == "Hi there!"

        # Second call - should be in cooldown
        response2 = await handle_command(mock_discord_message, mock_feature_flags)
        assert response2 is None


@pytest.mark.asyncio
async def test_cooldown_is_channel_specific(mock_twitch_message: MagicMock, mock_feature_flags: FeatureFlagsDB) -> None:
    # Setup
    command_name = "hello"
    bot_id = 1
    command_result = Result(
        ResultState.SUCCESS,
        BasicCommandDB(
            id=1,
            bot_id=bot_id,
            command=command_name,
            message="Hi there!",
            enabled=True,
            permission_level=PermissionLevel.USER,
        ),
    )

    with patch("bot.chat.handle_commands.get_command_core", return_value=command_result):
        # First call from channel 1
        mock_twitch_message.try_get_twitch_broadcaster_id.return_value = "channel1"
        response1 = await handle_command(mock_twitch_message, mock_feature_flags)
        assert response1 == "Hi there!"

        # Call from channel 2 - should also succeed
        mock_twitch_message.try_get_twitch_broadcaster_id.return_value = "channel2"
        response2 = await handle_command(mock_twitch_message, mock_feature_flags)
        assert response2 == "Hi there!"

        # Call from channel 1 again - should be in cooldown
        mock_twitch_message.try_get_twitch_broadcaster_id.return_value = "channel1"
        response3 = await handle_command(mock_twitch_message, mock_feature_flags)
        assert response3 is None


@pytest.mark.asyncio
async def test_cooldown_is_command_specific(mock_feature_flags: FeatureFlagsDB) -> None:
    # Setup
    bot_id = 1

    sender_chat = MagicMock()
    sender_chat.is_twitch = True
    sender_chat.is_discord = False

    original = MagicMock(spec=TwitchChatMessage)
    original.room = MagicMock()
    original.room.room_id = "12345"

    perm = PermissionLevel.USER

    msg = ChatMessage(
        bot_id=bot_id,
        text="!hello",
        sender=TwitchUserRef(name="test_user"),
        mentions=[],
        owner=TwitchUserRef(name="test_owner"),
        sender_chat=sender_chat,
        sender_permission_level=perm,
        original_message=original,
        meta_data=None,
    )
    # Patch to_response_message and id getters for easier testing
    msg.to_response_message = lambda x: x  # type: ignore[assignment]
    msg.try_get_twitch_broadcaster_id = MagicMock(return_value="12345")
    msg.try_get_discord_server_id = MagicMock(return_value=0)
    msg.try_get_discord_channel_id = MagicMock(return_value=0)

    def mock_get_command(msg: ChatMessage, name: str) -> Result[BasicCommandDB]:
        if name == "hello":
            return Result(
                ResultState.SUCCESS,
                BasicCommandDB(
                    id=1,
                    bot_id=msg.bot_id,
                    command="hello",
                    message="Hi!",
                    enabled=True,
                    permission_level=PermissionLevel.USER,
                ),
            )
        if name == "bye":
            return Result(
                ResultState.SUCCESS,
                BasicCommandDB(
                    id=2,
                    bot_id=msg.bot_id,
                    command="bye",
                    message="Goodbye!",
                    enabled=True,
                    permission_level=PermissionLevel.USER,
                ),
            )
        return Result(ResultState.NO_DATA)

    with patch("bot.chat.handle_commands.get_command_core", side_effect=mock_get_command):
        # Call !hello
        msg.text = "!hello"
        response1 = await handle_command(msg, mock_feature_flags)
        assert response1 == "Hi!"

        # Call !bye - should succeed even if !hello is in cooldown
        msg.text = "!bye"
        response2 = await handle_command(msg, mock_feature_flags)
        assert response2 == "Goodbye!"

        # Call !hello again - should be in cooldown
        msg.text = "!hello"
        response3 = await handle_command(msg, mock_feature_flags)
        assert response3 is None


@pytest.mark.asyncio
async def test_basic_command_permission_same_level_allowed(
    mock_twitch_message: MagicMock, mock_feature_flags: FeatureFlagsDB
) -> None:
    mock_twitch_message.sender_permission_level = PermissionLevel.SPECIAL_USER

    command_result = Result(
        ResultState.SUCCESS,
        BasicCommandDB(
            id=1,
            bot_id=mock_twitch_message.bot_id,
            command="hello",
            message="Hi there!",
            enabled=True,
            permission_level=PermissionLevel.SPECIAL_USER,
        ),
    )

    with patch("bot.chat.handle_commands.get_command_core", return_value=command_result):
        response = await handle_command(mock_twitch_message, mock_feature_flags)
        assert response == "Hi there!"


@pytest.mark.asyncio
async def test_basic_command_permission_higher_level_allowed(
    mock_twitch_message: MagicMock, mock_feature_flags: FeatureFlagsDB
) -> None:
    mock_twitch_message.sender_permission_level = PermissionLevel.MODERATOR

    command_result = Result(
        ResultState.SUCCESS,
        BasicCommandDB(
            id=1,
            bot_id=mock_twitch_message.bot_id,
            command="hello",
            message="Hi there!",
            enabled=True,
            permission_level=PermissionLevel.SPECIAL_USER,
        ),
    )

    with patch("bot.chat.handle_commands.get_command_core", return_value=command_result):
        response = await handle_command(mock_twitch_message, mock_feature_flags)
        assert response == "Hi there!"


@pytest.mark.asyncio
async def test_basic_command_permission_lower_level_denied(
    mock_twitch_message: MagicMock, mock_feature_flags: FeatureFlagsDB
) -> None:
    mock_twitch_message.sender_permission_level = PermissionLevel.USER

    command_result = Result(
        ResultState.SUCCESS,
        BasicCommandDB(
            id=1,
            bot_id=mock_twitch_message.bot_id,
            command="hello",
            message="Hi there!",
            enabled=True,
            permission_level=PermissionLevel.MODERATOR,
        ),
    )

    with patch("bot.chat.handle_commands.get_command_core", return_value=command_result):
        response = await handle_command(mock_twitch_message, mock_feature_flags)
        assert response == "You are not allowed to use this command. " + "This command has MODERATOR permission level."
