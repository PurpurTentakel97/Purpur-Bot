# pyright: reportPrivateUsage=false
from unittest.mock import MagicMock
from unittest.mock import patch

import discord

from bot.discord_bot.discord_server import DiscordServer


def test_discord_server_init() -> None:
    id_ = 1
    server_id = 123456789
    server = DiscordServer(id_, server_id)

    assert server.id == id_
    assert server.server_id == server_id


def test_discord_server_on_message() -> None:
    id_ = 1
    server_id = 123456789
    server = DiscordServer(id_, server_id)
    mock_message = MagicMock(spec=discord.Message)
    mock_message.author = "test_user"
    mock_message.content = "test_content"

    with patch("bot.discord_bot.discord_server.log_discord") as mock_log:
        server.on_message(mock_message)
        mock_log.assert_called_once()
        # Log message contains server_id, author and content
        log_msg = mock_log.call_args[0][1]
        assert str(server_id) in log_msg
        assert "test_user" in log_msg
        assert "test_content" in log_msg
