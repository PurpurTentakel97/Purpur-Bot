from unittest.mock import AsyncMock
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from bot.chat.message_handler import _handle_message_safely  # type: ignore[reportPrivateUsage]


@pytest.mark.asyncio
async def test_handle_message_safely_swallows_exceptions() -> None:
    message = MagicMock()
    message.text = "!quote"

    with patch(
        "bot.chat.message_handler.handle_single_message",
        new_callable=AsyncMock,
        side_effect=RuntimeError("boom"),
    ):
        await _handle_message_safely(message)  # must not raise


@pytest.mark.asyncio
async def test_handle_message_safely_sends_responses() -> None:
    message = MagicMock()
    response = MagicMock()

    with (
        patch(
            "bot.chat.message_handler.handle_single_message",
            new_callable=AsyncMock,
            return_value=[response],
        ),
        patch("bot.chat.message_handler._send_responses", new_callable=AsyncMock) as mock_send,
    ):
        await _handle_message_safely(message)

    mock_send.assert_awaited_once_with([response])
