import asyncio
from typing import Optional, Self

import discord

from discord_bot.discord_client import DiscordClient


class DiscordChat:
    def __init__(self, client: DiscordClient, token: str) -> None:
        self._client: DiscordClient = client
        self._token:str = token
        self._task:Optional[asyncio.Task] = None

    async def _ensure_connected(self) -> None:
        if self._task is None or self._task.done():
            self._task = await asyncio.create_task(self._client.start(self._token))


    @classmethod
    async def create(cls, token:str) -> Self:
        intents = discord.Intents.default()
        intents.message_content = True

        client = DiscordClient(intents=intents)

        instance = cls(client, token)
        await instance._ensure_connected()
        return instance
