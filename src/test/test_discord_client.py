# pyright: reportPrivateUsage=false
from unittest.mock import AsyncMock
from unittest.mock import MagicMock
from unittest.mock import PropertyMock
from unittest.mock import patch

import discord
import pytest

from bot.chat.discord_client import DiscordClient
from bot.chat.discord_server import DiscordServer
from bot.helpers.log import LogLevel


@pytest.fixture
def discord_client() -> DiscordClient:
    intents = discord.Intents.default()
    return DiscordClient(intents=intents, token="test_token")


@pytest.mark.asyncio
async def test_discord_client_init(discord_client: DiscordClient) -> None:
    assert discord_client._token == "test_token"
    assert discord_client._servers == {}


def test_discord_client_connect_chat(discord_client: DiscordClient) -> None:
    mock_server = MagicMock(spec=DiscordServer)
    mock_server.server_id = 12345
    discord_client.connect_chat(mock_server)
    assert discord_client._servers[12345] == mock_server


@pytest.mark.asyncio
async def test_discord_client_create() -> None:
    with (
        patch("bot.chat.discord_client.APP_CONTEXT") as mock_ctx,
        patch("bot.chat.discord_client.DiscordClient._start") as mock_start,
        patch("bot.chat.discord_client.DiscordClient.login", new_callable=AsyncMock) as mock_login,
    ):
        mock_ctx.discord_token.is_valid.return_value = True
        mock_ctx.discord_token.value_or_rise.return_value = "another_token"

        client = await DiscordClient.create()
        assert client is not None
        assert client._token == "another_token"
        mock_login.assert_called_once_with("another_token")
        mock_start.assert_called_once()
        assert isinstance(client, DiscordClient)


@pytest.mark.asyncio
async def test_discord_client_create_no_token() -> None:
    with (
        patch("bot.chat.discord_client.APP_CONTEXT") as mock_ctx,
        patch("bot.chat.discord_client.log_discord") as mock_log,
    ):
        mock_ctx.discord_token.is_valid.return_value = False

        client = await DiscordClient.create()
        assert client is None
        mock_log.assert_called_once()
        assert "Discord token not found" in mock_log.call_args[0][1]


@pytest.mark.asyncio
async def test_discord_client_create_login_failure() -> None:
    with (
        patch("bot.chat.discord_client.APP_CONTEXT") as mock_ctx,
        patch("bot.chat.discord_client.DiscordClient.login", new_callable=AsyncMock) as mock_login,
        patch("bot.chat.discord_client.log_discord") as mock_log,
    ):
        mock_ctx.discord_token.is_valid.return_value = True
        mock_ctx.discord_token.value_or_rise.return_value = "invalid_token"
        mock_login.side_effect = discord.LoginFailure("Improper token has been passed.")

        client = await DiscordClient.create()
        assert client is None
        mock_log.assert_called_with(LogLevel.ERROR, "Discord login failed: Improper token has been passed.")


@pytest.mark.asyncio
async def test_discord_client_on_ready(discord_client: DiscordClient) -> None:
    with patch("bot.chat.discord_client.log_discord") as mock_log:
        await discord_client.on_ready()
        mock_log.assert_called_once()
        assert "ready" in mock_log.call_args[0][1]


@pytest.mark.asyncio
async def test_on_message_ignore_self(discord_client: DiscordClient) -> None:
    mock_message = MagicMock(spec=discord.Message)
    # Using PropertyMock for a user because it's usually a property of discord.Client
    with patch.object(DiscordClient, "user", new_callable=PropertyMock) as mock_user:
        mock_user.return_value = MagicMock()
        mock_message.author = mock_user.return_value

        with patch("bot.chat.discord_client.log_discord") as mock_log:
            await discord_client.on_message(mock_message)
            mock_log.assert_not_called()


@pytest.mark.asyncio
async def test_on_message_dm(discord_client: DiscordClient) -> None:
    mock_message = MagicMock(spec=discord.Message)
    mock_message.author = "dm_user"
    mock_message.content = "dm_content"
    mock_message.guild = None

    with patch.object(DiscordClient, "user", new_callable=PropertyMock) as mock_user:
        mock_user.return_value = MagicMock()

        with patch("bot.chat.discord_client.log_discord") as mock_log:
            await discord_client.on_message(mock_message)
            # Should log DM
            assert any("DM | dm_user: dm_content" in str(call) for call in mock_log.call_args_list)


@pytest.mark.asyncio
async def test_on_message_server_not_found(discord_client: DiscordClient) -> None:
    mock_message = MagicMock(spec=discord.Message)
    mock_message.author = "server_user"
    mock_message.content = "server_content"
    mock_guild = MagicMock()
    mock_guild.id = 999
    mock_message.guild = mock_guild

    with patch.object(DiscordClient, "user", new_callable=PropertyMock) as mock_user:
        mock_user.return_value = MagicMock()

        with patch("bot.chat.discord_client.log_discord") as mock_log:
            await discord_client.on_message(mock_message)
            # Should log error and debug message
            log_messages = [call[0][1] for call in mock_log.call_args_list]
            assert any("Server 999 not found" in msg for msg in log_messages)
            assert any("999 | server_user: server_content" in msg for msg in log_messages)


@pytest.mark.asyncio
async def test_on_message_delegate_to_server(discord_client: DiscordClient) -> None:
    mock_message = MagicMock(spec=discord.Message)
    mock_message.author = "server_user"
    mock_message.content = "server_content"
    mock_guild = MagicMock()
    mock_guild.id = 123
    mock_message.guild = mock_guild

    mock_server = MagicMock(spec=DiscordServer)
    mock_server.server_id = 123
    discord_client.connect_chat(mock_server)

    with patch.object(DiscordClient, "user", new_callable=PropertyMock) as mock_user:
        mock_user.return_value = MagicMock()

        await discord_client.on_message(mock_message)
        mock_server.on_message.assert_called_once_with(mock_message)
