import asyncio

from bot.discord_bot.discord_chat import DiscordChat
from bot.helpers.app_context import APP_CONTEXT
from bot.twitch_bot.twitch_chat import TwitchChat
from bot.twitch_bot.twitch_client import TwitchClient


async def main() -> None:
    _: DiscordChat = await DiscordChat.create(APP_CONTEXT.discord_token)

    twitch_client = await TwitchClient.create()
    __ = await TwitchChat.create(twitch_client, "codingPurpurTentakel")

    while True:
        await asyncio.sleep(1)


def start() -> None:
    asyncio.run(main())


if __name__ == "__main__":
    start()
