from unittest.mock import AsyncMock
from unittest.mock import MagicMock
from unittest.mock import PropertyMock
from unittest.mock import patch

import discord
import pytest
from discord.abc import Messageable

from bot.discord_bot.discord_client import DiscordClient


@pytest.fixture
def discord_client() -> DiscordClient:
    intents = discord.Intents.default()
    return DiscordClient(intents=intents)


@pytest.mark.asyncio
async def test_send_message_success(discord_client: DiscordClient) -> None:
    channel_id = 123
    mock_channel = MagicMock(spec=Messageable)
    mock_channel.send = AsyncMock()

    with patch.object(discord_client, "get_channel", return_value=mock_channel):
        await discord_client.send_message(channel_id, "hello")
        mock_channel.send.assert_called_once_with("hello")


@pytest.mark.asyncio
async def test_send_message_channel_not_found(
    discord_client: DiscordClient, capsys: pytest.CaptureFixture[str]
) -> None:
    channel_id = 123

    with patch.object(discord_client, "get_channel", return_value=None):
        await discord_client.send_message(channel_id, "hello")

    captured = capsys.readouterr()
    assert f"Channel {channel_id} not found" in captured.out


@pytest.mark.asyncio
async def test_send_message_not_messageable(discord_client: DiscordClient, capsys: pytest.CaptureFixture[str]) -> None:
    channel_id = 123
    mock_channel = MagicMock()  # Not Messageable

    with patch.object(discord_client, "get_channel", return_value=mock_channel):
        await discord_client.send_message(channel_id, "hello")

    captured = capsys.readouterr()
    assert f"Channel {channel_id} is not a Message-able entity" in captured.out


@pytest.mark.asyncio
async def test_on_ready(discord_client: DiscordClient, capsys: pytest.CaptureFixture[str]) -> None:
    await discord_client.on_ready()
    captured = capsys.readouterr()
    assert "Discord client is ready!" in captured.out


@pytest.mark.asyncio
async def test_on_message_ignore_self(discord_client: DiscordClient) -> None:
    mock_message = MagicMock(spec=discord.Message)
    mock_message.author = discord_client.user

    # If it returns early, log_discord won't be called (we check via capsys or mocking log)
    with patch("bot.discord_bot.discord_client.log_discord") as mock_log:
        await discord_client.on_message(mock_message)
        mock_log.assert_not_called()


@pytest.mark.asyncio
async def test_on_message_log_others(discord_client: DiscordClient, capsys: pytest.CaptureFixture[str]) -> None:
    mock_message = MagicMock(spec=discord.Message)
    mock_message.author = "someone"
    mock_message.content = "hello bot"

    with patch("discord.Client.user", new_callable=PropertyMock) as mock_user:
        mock_user.return_value = "bot_user"
        await discord_client.on_message(mock_message)

    captured = capsys.readouterr()
    assert "someone: hello bot" in captured.out


@pytest.mark.asyncio
async def test_on_error_with_exception(discord_client: DiscordClient, capsys: pytest.CaptureFixture[str]) -> None:
    error_msg = "test error"
    try:
        raise ValueError(error_msg)
    except ValueError:
        # sys.exc_info() will be populated
        await discord_client.on_error("on_message")

    captured = capsys.readouterr()
    assert "ValueError" in captured.out
    assert "Error in event: on_message" in captured.out
    assert error_msg in captured.out


@pytest.mark.asyncio
async def test_on_error_without_exception(discord_client: DiscordClient, capsys: pytest.CaptureFixture[str]) -> None:
    # Ensure sys.exc_info returns (None, None, None)
    with patch("sys.exc_info", return_value=(None, None, None)):
        await discord_client.on_error("on_message", "arg1", kwarg1="val1")

    captured = capsys.readouterr()
    assert "Discord client error: on_message ('arg1',) {'kwarg1': 'val1'}" in captured.out
