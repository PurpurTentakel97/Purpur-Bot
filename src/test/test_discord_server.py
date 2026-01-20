# pyright: reportPrivateUsage=false


from unittest.mock import AsyncMock
from unittest.mock import MagicMock
from unittest.mock import patch

import discord
import pytest

from bot.chat.discord_server import DiscordServer


def test_discord_server_init() -> None:
    id_ = 1
    server_id = 123456789
    server = DiscordServer(id_, server_id)

    assert server.bot_id == id_
    assert server.server_id == server_id


@pytest.mark.asyncio
async def test_discord_server_on_message() -> None:
    id_ = 1
    server_id = 123456789
    server = DiscordServer(id_, server_id)
    mock_message = MagicMock(spec=discord.Message)
    mock_author = MagicMock(spec=discord.Member)
    mock_author.name = "test_user"
    mock_author.guild_permissions.administrator = False
    mock_author.guild_permissions.manage_messages = False
    mock_author.roles = []
    mock_message.author = mock_author
    mock_message.content = "test_content"

    await server.on_message(mock_message)
    assert server.message_queue.qsize() == 1
    msg = await server.message_queue.get()
    assert msg.text == "test_content"
    assert msg.sender_chat == server


@pytest.mark.asyncio
async def test_discord_server_permissions() -> None:
    from bot.core.types.permission_level import PermissionLevel

    id_ = 1
    server_id = 123456789
    server = DiscordServer(id_, server_id)

    # Admin
    mock_admin = MagicMock(spec=discord.Message)
    mock_admin.author = MagicMock(spec=discord.Member)
    mock_admin.author.guild_permissions.administrator = True
    mock_admin.content = "admin"
    await server.on_message(mock_admin)
    msg = await server.message_queue.get()
    assert msg.sender_permission_level == PermissionLevel.ADMIN

    # Moderator
    mock_mod = MagicMock(spec=discord.Message)
    mock_mod.author = MagicMock(spec=discord.Member)
    mock_mod.author.guild_permissions.administrator = False
    mock_mod.author.guild_permissions.manage_messages = True
    mock_mod.content = "mod"
    await server.on_message(mock_mod)
    msg = await server.message_queue.get()
    assert msg.sender_permission_level == PermissionLevel.MODERATOR

    # Special User (VIP role)
    mock_vip = MagicMock(spec=discord.Message)
    mock_vip.author = MagicMock(spec=discord.Member)
    mock_vip.author.guild_permissions.administrator = False
    mock_vip.author.guild_permissions.manage_messages = False
    mock_role = MagicMock(spec=discord.Role)
    mock_role.name = "vip"
    mock_vip.author.roles = [mock_role]
    mock_vip.content = "vip"
    await server.on_message(mock_vip)
    msg = await server.message_queue.get()
    assert msg.sender_permission_level == PermissionLevel.SPECIAL_USER

    # Normal User
    mock_user = MagicMock(spec=discord.Message)
    mock_user.author = MagicMock(spec=discord.Member)
    mock_user.author.guild_permissions.administrator = False
    mock_user.author.guild_permissions.manage_messages = False
    mock_user.author.roles = []
    mock_user.content = "user"
    await server.on_message(mock_user)
    msg = await server.message_queue.get()
    assert msg.sender_permission_level == PermissionLevel.USER


@pytest.mark.asyncio
async def test_discord_server_send_response_type_mismatch() -> None:
    from bot.chat.types.message_response import ChatMessageResponse

    id_ = 1
    server_id = 123456789
    server = DiscordServer(id_, server_id)

    # Use a non-DiscordMessage as original_message
    mock_bad_msg = MagicMock()
    responses = [ChatMessageResponse("msg", server, mock_bad_msg, None)]

    with patch("bot.chat.discord_server.log_discord") as mock_log:
        await server.send_response(responses)
        mock_log.assert_called_once()
        assert "type missmatch" in mock_log.call_args[0][1]


@pytest.mark.asyncio
async def test_discord_server_send_response_success() -> None:
    from bot.chat.types.message_response import ChatMessageResponse

    id_ = 1
    server_id = 123456789
    server = DiscordServer(id_, server_id)

    mock_channel = AsyncMock()
    mock_discord_msg = MagicMock(spec=discord.Message)
    mock_discord_msg.channel = mock_channel

    responses = [ChatMessageResponse("msg", server, mock_discord_msg, None)]
    await server.send_response(responses)

    mock_channel.send.assert_called_once_with("msg")


@pytest.mark.asyncio
async def test_discord_server_on_message_assertion_error() -> None:
    id_ = 1
    server_id = 123456789
    server = DiscordServer(id_, server_id)

    mock_message = MagicMock(spec=discord.Message)
    # author not a DiscordMember
    mock_message.author = MagicMock()

    with pytest.raises(AssertionError, match="Expected author to be a Member"):
        await server.on_message(mock_message)
