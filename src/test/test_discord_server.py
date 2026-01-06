# pyright: reportPrivateUsage=false


from unittest.mock import MagicMock

import discord
import pytest

from bot.chat.discord_server import DiscordServer


def test_discord_server_init() -> None:
    id_ = 1
    server_id = 123456789
    server = DiscordServer(id_, server_id)

    assert server.id == id_
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
