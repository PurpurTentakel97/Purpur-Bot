import asyncio

from helpers.config import load_config, Config
from discord_bot.discord_chat import DiscordChat
from twitch_bot.twitch_main import start_twitch_bot


async def main():
    config: Config = load_config()

    discord_bot: DiscordChat = await DiscordChat.create(config.discord_token)
    await start_twitch_bot(config.twitch_client_id, config.twitch_credentials)

    while True:
        await  asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
