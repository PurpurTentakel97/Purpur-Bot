from typing import final

import discord

from bot.helpers.log import LogLevel
from bot.helpers.log import log_discord


@final
class DiscordServer:
    def __init__(self, id_: int, server_id: int) -> None:
        self._id: int = id_
        self._server_id: int = server_id

    @property
    def id(self) -> int:
        return self._id

    @property
    def server_id(self) -> int:
        return self._server_id

    def on_message(self, message: discord.Message) -> None:
        log_discord(LogLevel.DEBUG, f"{self._server_id} | {message.author}: {message.content}")
