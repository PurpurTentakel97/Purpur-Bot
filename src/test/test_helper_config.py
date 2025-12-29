# pyright: reportPrivateUsage=false
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
from pydantic import ValidationError

from bot.helpers.config import ProgrammConfig
from bot.helpers.config import UserConfig
from bot.helpers.config import _save_default_config
from bot.helpers.config import get_config
from bot.helpers.log import LogLevel


def test_user_config_valid() -> None:
    user = UserConfig(id=1, name="test_user", twitch=["channel1", "channel2"], discord=[123, 456])
    assert user.id == 1
    assert user.name == "test_user"
    assert user.twitch == ["channel1", "channel2"]
    assert user.discord == [123, 456]


def test_user_config_invalid() -> None:
    with pytest.raises(ValidationError):
        UserConfig(id="not_an_int", name="test", twitch=[], discord=[])  # type: ignore[reportArgumentType]


def test_programm_config_valid() -> None:
    config = ProgrammConfig(
        user=[
            UserConfig(id=1, name="u1", twitch=[], discord=[]),
            UserConfig(id=2, name="u2", twitch=["t"], discord=[1]),
        ]
    )
    assert len(config.user) == 2
    assert config.user[0].id == 1
    assert config.user[1].name == "u2"


@patch("bot.helpers.config.PATH")
@patch("bot.helpers.config.log_default")
def test_save_default_config(mock_log: MagicMock, mock_path: MagicMock) -> None:
    mock_file = MagicMock()
    mock_path.open.return_value.__enter__.return_value = mock_file

    _save_default_config()

    mock_path.open.assert_called_once_with("w")
    mock_file.write.assert_called_once()
    mock_log.assert_called_once()
    assert "default config saved successfully" in mock_log.call_args[0][1]


@patch("bot.helpers.config.PATH")
@patch("bot.helpers.config.log_default")
def test_get_config_not_found(mock_log: MagicMock, mock_path: MagicMock) -> None:
    mock_path.exists.return_value = False

    # Mocking _save_default_config call inside get_config
    with patch("bot.helpers.config._save_default_config") as mock_save:
        config = get_config()
        assert config is None
        mock_save.assert_called_once()
        # Verify log calls
        log_messages = [call[0][1] for call in mock_log.call_args_list]
        assert any("config.json not found" in msg for msg in log_messages)
        assert any("Default config: Try to terminate" in msg for msg in log_messages)


@patch("bot.helpers.config.PATH")
@patch("bot.helpers.config.log_default")
def test_get_config_valid(mock_log: MagicMock, mock_path: MagicMock) -> None:
    mock_path.exists.return_value = True
    valid_json = '{"user": [{"id": 0, "name": "default", "twitch": ["t"], "discord": [0]}]}'
    mock_path.open.return_value.__enter__.return_value.read.return_value = valid_json

    config = get_config()
    assert config is not None
    assert len(config.user) == 1
    assert config.user[0].name == "default"

    mock_log.assert_called_with(LogLevel.INFO, "config loaded successfully")


@patch("bot.helpers.config.PATH")
@patch("bot.helpers.config.log_default")
def test_get_config_invalid_json(mock_log: MagicMock, mock_path: MagicMock) -> None:
    mock_path.exists.return_value = True
    invalid_json = '{"invalid": "data"}'
    mock_path.open.return_value.__enter__.return_value.read.return_value = invalid_json

    config = get_config()
    assert config is None

    # Check if an error was logged
    log_messages = [call[0][1] for call in mock_log.call_args_list]
    assert any("config.json is invalid" in msg for msg in log_messages)
