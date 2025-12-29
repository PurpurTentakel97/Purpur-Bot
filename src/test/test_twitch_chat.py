from unittest.mock import ANY
from unittest.mock import AsyncMock
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
from twitchAPI.chat import ChatEvent

from bot.twitch_bot.twitch_chat import TwitchChat


@pytest.mark.asyncio
async def test_twitch_chat_create() -> None:
    mock_twitch_client = MagicMock()
    mock_twitch_client.client = MagicMock()

    mock_chat_instance = MagicMock()
    # Mock Chat as an AsyncMock that returns another mock when called
    with patch("bot.twitch_bot.twitch_chat.Chat", new_callable=AsyncMock) as mock_chat_cls:
        mock_chat_cls.return_value = mock_chat_instance
        chat = await TwitchChat.create(mock_twitch_client, 1, "channel")

        assert isinstance(chat, TwitchChat)
        assert chat.id == 1
        assert chat.channel_name == "channel"
        mock_chat_cls.assert_called_once_with(mock_twitch_client.client)


@pytest.mark.asyncio
async def test_twitch_chat_init_registers_events() -> None:
    mock_chat = MagicMock()

    with (
        patch("bot.twitch_bot.twitch_chat.TwitchChat._on_ready", new_callable=AsyncMock),
        patch("bot.twitch_bot.twitch_chat.TwitchChat._on_message", new_callable=AsyncMock),
    ):
        _ = TwitchChat(mock_chat, 1, "channel")

        assert mock_chat.register_event.call_count == 2
        mock_chat.register_event.assert_any_call(ChatEvent.READY, ANY)
        mock_chat.register_event.assert_any_call(ChatEvent.MESSAGE, ANY)
        mock_chat.start.assert_called_once()


@pytest.mark.asyncio
async def test_twitch_chat_on_ready() -> None:
    mock_chat = MagicMock()
    chat = TwitchChat(mock_chat, 1, "channel")

    mock_event = MagicMock()
    mock_event.chat = AsyncMock()

    await chat._on_ready(mock_event)  # type: ignore[reportPrivateUsage]

    mock_event.chat.join_room.assert_called_once_with("channel")


@pytest.mark.asyncio
async def test_twitch_chat_on_message_no_command() -> None:
    mock_chat = MagicMock()
    chat = TwitchChat(mock_chat, 1, "channel")

    mock_message = MagicMock()
    mock_message.text = "Hello world"

    with patch.object(chat, "handle_command", new_callable=AsyncMock) as mock_handle:
        await chat._on_message(mock_message)  # type: ignore[reportPrivateUsage]
        mock_handle.assert_not_called()


@pytest.mark.asyncio
async def test_twitch_chat_on_message_command() -> None:
    mock_chat = MagicMock()
    chat = TwitchChat(mock_chat, 1, "channel")

    mock_message = MagicMock()
    mock_message.text = "!ping"

    with patch.object(chat, "handle_command", new_callable=AsyncMock) as mock_handle:
        await chat._on_message(mock_message)  # type: ignore[reportPrivateUsage]
        mock_handle.assert_called_once_with("!ping")


@pytest.mark.asyncio
async def test_twitch_chat_handle_command() -> None:
    mock_chat = MagicMock()
    mock_chat.send_message = AsyncMock()
    chat = TwitchChat(mock_chat, 1, "channel")

    await chat.handle_command("!any")

    mock_chat.send_message.assert_called_once_with("channel", "!ping")
