"""``handle_build_in_command`` matches on a lower-cased ``route`` copy but must
forward the *original* tokens untouched. These tests check exactly that: a
weird-cased / punctuated argument reaches the core function byte-for-byte, no
matter how the command word itself was cased.
"""

from unittest.mock import AsyncMock
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from bot.chat.handle_commands import handle_build_in_command
from bot.core.types.permission_level import PermissionLevel
from bot.core.types.result import Result
from bot.core.types.result import ResultState
from bot.database.types.feature_flags import FeatureFlagsDB


@pytest.fixture
def feature_flags() -> FeatureFlagsDB:
    return FeatureFlagsDB(
        id=1,
        bot_id=1,
        can_commands=True,
        can_alias=True,
        can_broadcast=True,
        can_twitch_live=True,
        can_quote=True,
    )


def _message(text: str) -> MagicMock:
    message = MagicMock()
    message.text = text
    message.bot_id = 1
    message.sender_permission_level = PermissionLevel.ADMIN
    message.has_twitch_message = True
    message.has_discord_message = False
    message.try_get_twitch_broadcaster_id = MagicMock(return_value="12345")
    message.try_get_discord_server_id = MagicMock(return_value=0)
    message.try_get_discord_channel_id = MagicMock(return_value=0)
    message.to_response_message = lambda text: text  # type: ignore[reportUnknownLambdaType, assignment]
    return message


@pytest.mark.asyncio
async def test_identifier_token_is_forwarded_untouched(feature_flags: FeatureFlagsDB) -> None:
    message = _message("!COM enable FoO_Bar-123")

    with patch("bot.chat.handle_commands.enable_command_by_bot_id_core") as mock_core:
        await handle_build_in_command(message, feature_flags)

    mock_core.assert_called_once_with(1, "FoO_Bar-123")


@pytest.mark.asyncio
async def test_free_text_payload_is_forwarded_untouched(feature_flags: FeatureFlagsDB) -> None:
    message = _message("!Com ADD greet Hello WORLD, stays MixedCase!")

    with patch("bot.chat.handle_commands.save_command_core") as mock_core:
        await handle_build_in_command(message, feature_flags)

    mock_core.assert_called_once_with(1, "greet", "Hello WORLD, stays MixedCase!")


@pytest.mark.asyncio
async def test_quote_lookup_name_is_forwarded_untouched(feature_flags: FeatureFlagsDB) -> None:
    message = _message("!QUOTE @LimQuats")
    get_mock = AsyncMock(return_value=Result(ResultState.SUCCESS, "a quote"))

    with patch("bot.chat.handle_commands.get_quote", new=get_mock):
        await handle_build_in_command(message, feature_flags)

    get_mock.assert_awaited_once_with("@LimQuats", message)
