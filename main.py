import asyncio

from src.discord_bot.discord_chat import DiscordChat
from src.helpers.config import Config
from src.helpers.config import load_config

# from twitch_bot.twitch_main import start_twitch_bot


async def main() -> None:
    config: Config = load_config()

    _: DiscordChat = await DiscordChat.create(config.discord_token)
    # await start_twitch_bot(config.twitch_client_id, config.twitch_credentials)

    while True:
        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
