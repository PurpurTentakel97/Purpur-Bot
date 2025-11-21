import discord
from discord import Client
from helpers.log import log_discord, LogLevel, log_exception, LogProgramm
import sys

class DiscordClient(Client):
    def __init__(self,
                 *,
                 intents: discord.Intents):
        super().__init__(intents=intents)

    async def send_message(self, channel_id: int, message: str) -> None:
        channel = self.get_channel(channel_id)
        if not channel:
            log_discord(LogLevel.ERROR, f"Channel {channel_id} not found!")
            return
        await channel.send(message)

    async def on_ready(self) -> None:
        log_discord(LogLevel.INFO, "Discord client is ready!")

    async def on_message(self, message: discord.Message) -> None:
        if message.author == self.user:
            return

        log_discord(LogLevel.DEBUG, f"{message.author}: {message.content}")

    async def on_error(self, event, *args, **kwargs) -> None:
        exc_type, value, traceback = sys.exc_info()

        if value:
            log_exception(value, LogProgramm.Discord, f"Error in event: {event}")
        else:
            log_discord(LogLevel.ERROR, f"Discord client error: {event} {args} {kwargs}")
