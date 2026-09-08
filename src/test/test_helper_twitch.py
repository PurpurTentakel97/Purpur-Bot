from collections.abc import Generator
from unittest.mock import AsyncMock
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
from twitchAPI.type import TwitchAPIException

from bot.chat.helper.twitch import get_user_by_id
from bot.chat.helper.twitch import get_user_by_name
from bot.core.types.result import ResultState


@pytest.fixture
def twitch_available() -> Generator[MagicMock, None, None]:
    with patch("bot.chat.helper.twitch.PROGRAMM_PARTS") as mock_parts:
        mock_parts.twitch = MagicMock()
        yield mock_parts


@pytest.mark.asyncio
async def test_get_user_by_id_success(twitch_available: MagicMock) -> None:
    user = MagicMock()
    with patch("bot.chat.helper.twitch.first", new_callable=AsyncMock, return_value=user):
        result = await get_user_by_id("123")

    assert result.state == ResultState.SUCCESS
    assert result.value is user


@pytest.mark.asyncio
async def test_get_user_by_id_none_is_user_not_found(twitch_available: MagicMock) -> None:
    with patch("bot.chat.helper.twitch.first", new_callable=AsyncMock, return_value=None):
        result = await get_user_by_id("123")

    assert result.state == ResultState.USER_NOT_FOUND


@pytest.mark.asyncio
async def test_get_user_by_id_api_error_is_caught(twitch_available: MagicMock) -> None:
    with patch("bot.chat.helper.twitch.first", new_callable=AsyncMock, side_effect=TwitchAPIException("Bad Request")):
        result = await get_user_by_id("12345678910")

    assert result.state == ResultState.ERROR


@pytest.mark.asyncio
async def test_get_user_by_id_timeout_is_caught(twitch_available: MagicMock) -> None:
    with patch("bot.chat.helper.twitch.first", new_callable=AsyncMock, side_effect=TimeoutError()):
        result = await get_user_by_id("123")

    assert result.state == ResultState.ERROR


@pytest.mark.asyncio
async def test_get_user_by_name_api_error_is_caught(twitch_available: MagicMock) -> None:
    with patch("bot.chat.helper.twitch.first", new_callable=AsyncMock, side_effect=TwitchAPIException("boom")):
        result = await get_user_by_name("someone")

    assert result.state == ResultState.ERROR


@pytest.mark.asyncio
async def test_get_user_by_id_without_client_is_error() -> None:
    with patch("bot.chat.helper.twitch.PROGRAMM_PARTS") as mock_parts:
        mock_parts.twitch = None
        result = await get_user_by_id("123")

    assert result.state == ResultState.ERROR
