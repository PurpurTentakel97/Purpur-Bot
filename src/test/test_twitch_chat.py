from unittest.mock import ANY
from unittest.mock import AsyncMock
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
from twitchAPI.chat import ChatEvent

from bot.chat.twitch_chat import TwitchChat


@pytest.mark.asyncio
async def test_twitch_chat_create() -> None:
    mock_twitch_client = MagicMock()
    mock_twitch_client.client = MagicMock()

    mock_chat_instance = MagicMock()
    # Mock TwitchChatClient as an AsyncMock that returns another mock when called
    with patch("bot.chat.twitch_chat.TwitchChatClient", new_callable=AsyncMock) as mock_chat_cls:
        mock_chat_cls.return_value = mock_chat_instance
        chat = await TwitchChat.create(mock_twitch_client, 1, "channel")

        assert isinstance(chat, TwitchChat)
        assert chat.bot_id == 1
        assert chat.channel_name == "channel"
        mock_chat_cls.assert_called_once_with(mock_twitch_client.client)


@pytest.mark.asyncio
async def test_twitch_chat_init_registers_events() -> None:
    mock_chat = MagicMock()

    with (
        patch("bot.chat.twitch_chat.TwitchChat._on_ready", new_callable=AsyncMock),
        patch("bot.chat.twitch_chat.TwitchChat._on_message", new_callable=AsyncMock),
    ):
        _ = TwitchChat(mock_chat, 1, "channel")

        assert mock_chat.register_event.call_count == 2
        mock_chat.register_event.assert_any_call(ChatEvent.READY, ANY)
        mock_chat.register_event.assert_any_call(ChatEvent.MESSAGE, ANY)
        mock_chat.start.assert_called_once()


@pytest.mark.asyncio
async def test_twitch_chat_on_ready() -> None:
    mock_chat = MagicMock()
    mock_chat.send_message = AsyncMock()
    chat = TwitchChat(mock_chat, 1, "channel")

    mock_event = MagicMock()
    mock_event.chat = AsyncMock()

    await chat._on_ready(mock_event)  # type: ignore[reportPrivateUsage]

    mock_event.chat.join_room.assert_called_once_with("channel")
    mock_chat.send_message.assert_called_once_with("channel", "Tentakel Bot joined")


@pytest.mark.asyncio
async def test_twitch_chat_on_message_no_command() -> None:
    mock_chat = MagicMock()
    chat = TwitchChat(mock_chat, 1, "channel")

    mock_message = MagicMock()
    mock_message.text = "Hello world"
    mock_message.user.mod = False
    mock_message.user.vip = False
    mock_message.user.badges = {}

    await chat._on_message(mock_message)  # type: ignore[reportPrivateUsage]
    assert chat.message_queue.qsize() == 1
    msg = await chat.message_queue.get()
    assert msg.text == "Hello world"


@pytest.mark.asyncio
async def test_twitch_chat_on_message_command() -> None:
    mock_chat = MagicMock()
    chat = TwitchChat(mock_chat, 1, "channel")

    mock_message = MagicMock()
    mock_message.text = "!ping"
    mock_message.user.mod = False
    mock_message.user.vip = False
    mock_message.user.badges = {}

    await chat._on_message(mock_message)  # type: ignore[reportPrivateUsage]
    assert chat.message_queue.qsize() == 1
    msg = await chat.message_queue.get()
    assert msg.text == "!ping"


@pytest.mark.asyncio
async def test_twitch_chat_permissions() -> None:
    from bot.core.types.permission_level import PermissionLevel

    mock_chat = MagicMock()
    chat = TwitchChat(mock_chat, 1, "channel")

    # Admin (Broadcaster)
    mock_admin = MagicMock()
    mock_admin.text = "admin msg"
    mock_admin.user.mod = False
    mock_admin.user.vip = False
    mock_admin.user.badges = {"broadcaster": "1"}
    await chat._on_message(mock_admin)  # type: ignore[reportPrivateUsage]
    msg = await chat.message_queue.get()
    assert msg.sender_permission_level == PermissionLevel.ADMIN

    # Moderator
    mock_mod = MagicMock()
    mock_mod.text = "mod msg"
    mock_mod.user.mod = True
    mock_mod.user.vip = False
    mock_mod.user.badges = {}
    await chat._on_message(mock_mod)  # type: ignore[reportPrivateUsage]
    msg = await chat.message_queue.get()
    assert msg.sender_permission_level == PermissionLevel.MODERATOR

    # Special User (VIP)
    mock_vip = MagicMock()
    mock_vip.text = "vip msg"
    mock_vip.user.mod = False
    mock_vip.user.vip = True
    mock_vip.user.badges = {}
    await chat._on_message(mock_vip)  # type: ignore[reportPrivateUsage]
    msg = await chat.message_queue.get()
    assert msg.sender_permission_level == PermissionLevel.SPECIAL_USER

    # Normal User
    mock_user = MagicMock()
    mock_user.text = "user msg"
    mock_user.user.mod = False
    mock_user.user.vip = False
    mock_user.user.badges = {}
    await chat._on_message(mock_user)  # type: ignore[reportPrivateUsage]
    msg = await chat.message_queue.get()
    assert msg.sender_permission_level == PermissionLevel.USER


@pytest.mark.asyncio
async def test_twitch_chat_terminate() -> None:
    mock_chat = MagicMock()
    mock_chat.send_message = AsyncMock()
    chat = TwitchChat(mock_chat, 1, "channel")
    await chat.terminate(mock_chat)
    mock_chat.stop.assert_called_once()
    mock_chat.send_message.assert_called_once_with("channel", "Tentakel Bot left")


@pytest.mark.asyncio
async def test_twitch_chat_send_response() -> None:
    from bot.chat.types.message_response import ChatMessageResponse

    mock_chat = MagicMock()
    mock_chat.send_message = AsyncMock()
    chat = TwitchChat(mock_chat, 1, "channel")

    mock_original_message = MagicMock()
    responses = [
        ChatMessageResponse("msg1", chat, mock_original_message, None),
        ChatMessageResponse("msg2", chat, mock_original_message, None),
    ]
    await chat.send_response(responses)

    assert mock_chat.send_message.call_count == 2
    mock_chat.send_message.assert_any_call("channel", "msg1")
    mock_chat.send_message.assert_any_call("channel", "msg2")
