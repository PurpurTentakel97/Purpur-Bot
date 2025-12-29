import asyncio

from bot.discord_bot.discord_server import DiscordServer
from bot.discord_bot.discord_client import DiscordClient
from bot.helpers.app_context import APP_CONTEXT
from bot.twitch_bot.twitch_chat import TwitchChat
from bot.twitch_bot.twitch_client import TwitchClient


async def main() -> None:
    discord_client = await DiscordClient.create(APP_CONTEXT.discord_token)
    _ = DiscordServer(1, 1222634745448501330)
    discord_client.connect_chat(_)

    twitch_client = await TwitchClient.create()
    __ = await TwitchChat.create(twitch_client, "codingPurpurTentakel")

    while True:
        await asyncio.sleep(1)


def start() -> None:
    asyncio.run(main())


if __name__ == "__main__":
    start()
