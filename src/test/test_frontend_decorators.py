from dataclasses import dataclass
from http import HTTPStatus
from typing import Any
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from bot.core.types.result import Result
from bot.core.types.result import ResultState
from bot.database.types.bot_config import BotConfigDB
from bot.frontend.helpers.decorators import _get_owned_ressource  # pyright: ignore[reportPrivateUsage]
from bot.frontend.helpers.decorators import get_owned_bot
from bot.frontend.types.twitch_user_info import TwitchUserInfo


def test_get_owned_bot_success(monkeypatch: Any) -> None:
    mock_bot = BotConfigDB(id=1, twitch_user_id="123", name="testbot", enabled=True)
    mock_get_bot = MagicMock(return_value=Result(ResultState.SUCCESS, mock_bot))
    monkeypatch.setattr("bot.frontend.helpers.decorators.get_bot_core", mock_get_bot)

    twitch_user = TwitchUserInfo(id_="123", login="test", display_name="Test", profile_image_url="")

    result = get_owned_bot(1, twitch_user)
    assert result == mock_bot


def test_get_owned_bot_not_found(monkeypatch: Any) -> None:
    mock_get_bot = MagicMock(return_value=Result(ResultState.NO_DATA, None))
    monkeypatch.setattr("bot.frontend.helpers.decorators.get_bot_core", mock_get_bot)

    twitch_user = TwitchUserInfo(id_="123", login="test", display_name="Test", profile_image_url="")

    with pytest.raises(HTTPException) as excinfo:
        get_owned_bot(1, twitch_user)
    assert excinfo.value.status_code == HTTPStatus.NOT_FOUND


def test_get_owned_bot_forbidden(monkeypatch: Any) -> None:
    mock_bot = BotConfigDB(id=1, twitch_user_id="456", name="testbot", enabled=True)
    mock_get_bot = MagicMock(return_value=Result(ResultState.SUCCESS, mock_bot))
    monkeypatch.setattr("bot.frontend.helpers.decorators.get_bot_core", mock_get_bot)

    twitch_user = TwitchUserInfo(id_="123", login="test", display_name="Test", profile_image_url="")

    with pytest.raises(HTTPException) as excinfo:
        get_owned_bot(1, twitch_user)
    assert excinfo.value.status_code == HTTPStatus.FORBIDDEN


def test_get_owned_resource_success() -> None:
    @dataclass
    class Resource:
        id: int
        bot_id: int

    bot = BotConfigDB(id=1, twitch_user_id="123", name="testbot", enabled=True)
    resource = Resource(id=10, bot_id=1)

    mock_callable = MagicMock(return_value=Result(ResultState.SUCCESS, resource))

    result = _get_owned_ressource(10, mock_callable, bot)
    assert result == resource


def test_get_owned_resource_wrong_bot() -> None:
    @dataclass
    class Resource:
        id: int
        bot_id: int

    bot = BotConfigDB(id=1, twitch_user_id="123", name="testbot", enabled=True)
    resource = Resource(id=10, bot_id=2)  # Wrong bot_id

    mock_callable = MagicMock(return_value=Result(ResultState.SUCCESS, resource))

    with pytest.raises(HTTPException) as excinfo:
        _get_owned_ressource(10, mock_callable, bot)
    assert excinfo.value.status_code == HTTPStatus.FORBIDDEN


def test_get_owned_resource_not_found() -> None:
    bot = BotConfigDB(id=1, twitch_user_id="123", name="testbot", enabled=True)
    mock_callable = MagicMock(return_value=Result(ResultState.NO_DATA, None))

    with pytest.raises(HTTPException) as excinfo:
        _get_owned_ressource(10, mock_callable, bot)
    assert excinfo.value.status_code == HTTPStatus.NOT_FOUND
