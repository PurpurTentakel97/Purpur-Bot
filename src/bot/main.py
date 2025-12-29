import asyncio
from typing import Optional

from bot.discord_bot.discord_client import DiscordClient
from bot.discord_bot.discord_server import DiscordServer
from bot.twitch_bot.twitch_chat import TwitchChat
from bot.twitch_bot.twitch_client import TwitchClient

DEBUG_ID = 1


def _handle_console() -> None:
    while True:
        command = input()
        if command == "exit":
            break


async def _start_discord_bot() -> Optional[DiscordClient]:
    discord_client = await DiscordClient.create()

    if discord_client is None:
        return None

    discord_server = DiscordServer(DEBUG_ID, 1222634745448501330)
    discord_client.connect_chat(discord_server)
    return discord_client


async def _stop_discord_bot(discord_client: Optional[DiscordClient]) -> None:
    if discord_client is None:
        return

    await discord_client.terminate()


async def _start_twitch_bot() -> Optional[TwitchClient]:
    twitch_client = await TwitchClient.create()

    if twitch_client is None:
        return None

    await TwitchChat.create(twitch_client, DEBUG_ID, "codingPurpurTentakel")
    return twitch_client


async def _stop_twitch_bot(twitch_client: Optional[TwitchClient]) -> None:
    if twitch_client is None:
        return

    await twitch_client.terminate()


async def main() -> None:
    discord_client: Optional[DiscordClient] = await _start_discord_bot()
    twitch_client: Optional[TwitchClient] = await _start_twitch_bot()

    _handle_console()  # blocking

    await _stop_discord_bot(discord_client)
    await _stop_twitch_bot(twitch_client)


def start() -> None:
    asyncio.run(main())


if __name__ == "__main__":
    start()
