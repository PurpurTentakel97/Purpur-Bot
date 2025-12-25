import asyncio

from bot.discord_bot.discord_chat import DiscordChat
from bot.helpers.config import Config
from bot.helpers.config import load_config


async def main() -> None:
    config: Config = load_config()

    _: DiscordChat = await DiscordChat.create(config.discord_token)

    while True:
        await asyncio.sleep(1)


def start() -> None:
    asyncio.run(main())

if __name__ == "__main__":
    start()
