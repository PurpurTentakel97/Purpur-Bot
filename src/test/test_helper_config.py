from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from bot.helpers.config import Config
from bot.helpers.config import load_config
from bot.helpers.file import FileResultType
from bot.helpers.file import LoadJsonResult
from bot.helpers.file import SaveJsonResult


def test_config_defaults() -> None:
    config = Config()
    assert config.discord_token == "<DISCORD_TOKEN>"
    assert config.twitch_client_id == "<TWITCH_CLIENT_ID>"
    assert config.twitch_credentials == "<TWITCH_CREDENTIALS>"


@patch("bot.helpers.config.load_json")
def test_load_config_success(mock_load_json: MagicMock) -> None:
    # Setup mocks
    # First call for sample config
    # Second call for actual config
    mock_load_json.side_effect = [
        LoadJsonResult(FileResultType.SUCCESS, Config()),
        LoadJsonResult(FileResultType.SUCCESS, Config(discord_token="real_token")),
    ]

    config = load_config()

    assert config.discord_token == "real_token"
    assert mock_load_json.call_count == 2


@patch("bot.helpers.config.save_json")
@patch("bot.helpers.config.load_json")
def test_load_config_sample_missing_then_success(mock_load_json: MagicMock, mock_save_json: MagicMock) -> None:
    # Setup mocks
    # 1. load sample fails
    # 2. save sample succeeds
    # 3. load config succeeds
    mock_load_json.side_effect = [
        LoadJsonResult(FileResultType.FILE_NOT_FOUND, None),
        LoadJsonResult(FileResultType.SUCCESS, Config(discord_token="real_token")),
    ]
    mock_save_json.return_value = SaveJsonResult(FileResultType.SUCCESS)

    config = load_config()

    assert config.discord_token == "real_token"
    assert mock_load_json.call_count == 2
    mock_save_json.assert_called_once()


@patch("bot.helpers.config.load_json")
def test_load_config_fail_raises_exception(mock_load_json: MagicMock) -> None:
    # Setup mocks
    # load sample succeeds
    # load config fails
    mock_load_json.side_effect = [
        LoadJsonResult(FileResultType.SUCCESS, Config()),
        LoadJsonResult(FileResultType.FILE_NOT_FOUND, None),
    ]

    with pytest.raises(Exception, match="Failed to load config"):
        load_config()
