import asyncio

from bot.discord_bot.discord_chat import DiscordChat
from bot.helpers.app_context import APP_CONTEXT


async def main() -> None:
    _: DiscordChat = await DiscordChat.create(APP_CONTEXT.discord_token)

    while True:
        await asyncio.sleep(1)


def start() -> None:
    asyncio.run(main())


if __name__ == "__main__":
    start()
