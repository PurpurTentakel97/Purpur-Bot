import asyncio
from typing import Self
from typing import final

import discord
from discord import Client

from bot.discord_bot.discord_server import DiscordServer
from bot.helpers.log import LogLevel
from bot.helpers.log import log_discord


@final
class DiscordClient(Client):
    def __init__(self, *, intents: discord.Intents, token: str) -> None:
        super().__init__(intents=intents)
        self._token: str = token
        self._servers: dict[int, DiscordServer] = {}

    def connect_chat(self, chat: DiscordServer) -> None:
        self._servers[chat.server_id] = chat

    def _start(self) -> None:
        log_discord(LogLevel.INFO, "Connecting to Discord...")
        asyncio.create_task(self.start(self._token))

    @classmethod
    async def create(cls, token: str) -> Self:
        intents = discord.Intents.default()
        intents.message_content = True

        instance = cls(intents=intents, token=token)
        instance._start()

        return instance

    async def on_ready(self) -> None:
        log_discord(LogLevel.INFO, "Discord client is ready!")

    async def on_disconnect(self) -> None:
        log_discord(LogLevel.ERROR, "Discord client disconnected!")

    async def on_resumed(self) -> None:
        log_discord(LogLevel.INFO, "Discord client resumed!")

    async def on_message(self, message: discord.Message) -> None:
        if message.author == self.user:
            return

        incoming_server_id = message.guild.id if message.guild else None

        if incoming_server_id is None:
            log_discord(LogLevel.DEBUG, f"DM | {message.author}: {message.content}")
            return

        if incoming_server_id not in self._servers:
            log_discord(LogLevel.ERROR, f"Server {incoming_server_id} not found in chats")
            log_discord(LogLevel.DEBUG, f"{incoming_server_id} | {message.author}: {message.content}")
            return

        self._servers[incoming_server_id].on_message(message)
