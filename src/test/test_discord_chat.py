# pyright: reportPrivateUsage=false
import asyncio
from unittest.mock import AsyncMock
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from bot.discord_bot.discord_chat import DiscordChat
from bot.discord_bot.discord_client import DiscordClient


@pytest.mark.asyncio
async def test_discord_chat_init() -> None:
    mock_client = MagicMock(spec=DiscordClient)
    token = "test_token"
    chat = DiscordChat(mock_client, token)

    assert chat._client == mock_client
    assert chat._token == token
    assert chat._task is None


@pytest.mark.asyncio
async def test_ensure_connected_new_task() -> None:
    mock_client = MagicMock(spec=DiscordClient)
    mock_client.start = AsyncMock()
    token = "test_token"
    chat = DiscordChat(mock_client, token)

    with patch("asyncio.create_task") as mock_create_task:
        await chat._ensure_connected()
        mock_create_task.assert_called_once()
        assert chat._task is not None


@pytest.mark.asyncio
async def test_ensure_connected_already_running() -> None:
    mock_client = MagicMock(spec=DiscordClient)
    token = "test_token"
    chat = DiscordChat(mock_client, token)

    mock_task = MagicMock(spec=asyncio.Task)
    mock_task.done.return_value = False
    chat._task = mock_task

    with patch("asyncio.create_task") as mock_create_task:
        await chat._ensure_connected()
        mock_create_task.assert_not_called()


@pytest.mark.asyncio
async def test_ensure_connected_task_done() -> None:
    mock_client = MagicMock(spec=DiscordClient)
    mock_client.start = AsyncMock()
    token = "test_token"
    chat = DiscordChat(mock_client, token)

    mock_task = MagicMock(spec=asyncio.Task)
    mock_task.done.return_value = True
    chat._task = mock_task

    with patch("asyncio.create_task") as mock_create_task:
        await chat._ensure_connected()
        mock_create_task.assert_called_once()


@pytest.mark.asyncio
async def test_discord_chat_create() -> None:
    token = "test_token"

    with patch("bot.discord_bot.discord_chat.DiscordClient") as mock_client_cls:
        mock_client_instance = mock_client_cls.return_value

        # We need to mock _ensure_connected or the things it calls
        with patch.object(DiscordChat, "_ensure_connected", new_callable=AsyncMock) as mock_ensure:
            chat = await DiscordChat.create(token)

            mock_client_cls.assert_called_once()
            mock_ensure.assert_called_once()
            assert isinstance(chat, DiscordChat)
            assert chat._token == token
            assert chat._client == mock_client_instance
