import sys
from typing import Any

import discord
from discord import Client
from discord.abc import Messageable

from bot.helpers.log import LogLevel
from bot.helpers.log import LogProgram
from bot.helpers.log import log_discord
from bot.helpers.log import log_exception


class DiscordClient(Client):
    def __init__(self, *, intents: discord.Intents) -> None:
        super().__init__(intents=intents)

    async def send_message(self, channel_id: int, message: str) -> None:
        channel = self.get_channel(channel_id)
        if isinstance(channel, Messageable):
            await channel.send(message)
            return

        if not channel:
            log_discord(LogLevel.ERROR, f"Channel {channel_id} not found")
            return

        log_discord(LogLevel.ERROR, f"Channel {channel_id} is not a Message-able entity")

    async def on_ready(self) -> None:
        log_discord(LogLevel.INFO, "Discord client is ready!")

    async def on_message(self, message: discord.Message) -> None:
        if message.author == self.user:
            return

        log_discord(LogLevel.DEBUG, f"{message.author}: {message.content}")

    async def on_error(self, event: str, *args: Any, **kwargs: Any) -> None:
        # exc_type , value, traceback
        _, value, _ = sys.exc_info()

        if value:
            log_exception(value, LogProgram.Discord, f"Error in event: {event}")
        else:
            log_discord(LogLevel.ERROR, f"Discord client error: {event} {args} {kwargs}")
