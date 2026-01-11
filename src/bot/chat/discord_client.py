import asyncio
from typing import Optional
from typing import Self
from typing import final

import discord
from discord import Client

from bot.chat.discord_server import DiscordServer
from bot.chat.types.message import ChatMessage
from bot.core.app_context import APP_CONTEXT
from bot.helpers.log import LogLevel
from bot.helpers.log import log_discord


@final
class DiscordClient(Client):
    def __init__(self, *, intents: discord.Intents, token: str) -> None:
        super().__init__(intents=intents)
        self._token: str = token
        self._servers: dict[int, DiscordServer] = {}
        self._connection_task: Optional[asyncio.Task[None]] = None

    async def get_next_message(self) -> Optional[ChatMessage]:
        for server in self._servers.values():
            message = await server.get_next_message()
            if message is not None:
                return message
        return None

    @property
    def servers(self) -> list[DiscordServer]:
        return list(self._servers.values())

    async def leave_guild(self, server_id: int) -> bool:
        guild = self.get_guild(server_id)
        if guild is None:
            log_discord(LogLevel.WARNING, f"Could not leave guild {server_id}: Guild not found.")
            return False

        try:
            await guild.leave()
            log_discord(LogLevel.INFO, f"Left guild {server_id}.")
            return True
        except discord.HTTPException as e:
            log_discord(LogLevel.ERROR, f"Failed to leave guild {server_id}: {e}")
            return False

    def connect_server(self, server: DiscordServer) -> None:
        self._servers[server.server_id] = server
        log_discord(LogLevel.INFO, f"Server {server.server_id} initialized.")

    def remove_server(self, server: DiscordServer) -> None:
        del self._servers[server.server_id]
        log_discord(LogLevel.INFO, f"Server {server.server_id} terminated.")

    def _start(self) -> None:
        log_discord(LogLevel.INFO, "Connecting to Discord...")
        self._connection_task = asyncio.create_task(self.connect())

    async def terminate(self) -> None:
        await self.close()
        if self._connection_task is not None:
            self._connection_task.cancel()
            try:
                await self._connection_task
            except asyncio.CancelledError:
                pass
        log_discord(LogLevel.INFO, "Discord client terminated.")

    @classmethod
    async def create(cls) -> Optional[Self]:
        if not APP_CONTEXT.discord_token.is_valid():
            log_discord(LogLevel.ERROR, "Discord token not found in environment variables. Discord Bot isn't started.")
            return None

        intents = discord.Intents.default()
        intents.message_content = True

        instance = cls(intents=intents, token=APP_CONTEXT.discord_token.value_or_rise())
        try:
            await instance.login(instance._token)
        except discord.LoginFailure as e:
            log_discord(LogLevel.ERROR, f"Discord login failed: {e}")
            return None

        instance._start()

        return instance

    async def on_ready(self) -> None:
        log_discord(LogLevel.INFO, "Discord client is ready!")

    async def on_disconnect(self) -> None:
        log_discord(LogLevel.INFO, "Discord client disconnected!")

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
            log_discord(
                LogLevel.ERROR,
                f"Server {incoming_server_id} ({type(incoming_server_id)}) not found in chats. "
                + f"Available: {list(self._servers.keys())}",
            )
            log_discord(LogLevel.DEBUG, f"{incoming_server_id} | {message.author}: {message.content}")
            return

        await self._servers[incoming_server_id].on_message(message)
