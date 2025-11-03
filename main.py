import asyncio
import os

from dotenv import load_dotenv
from discord_bot.discord_main import start_discord_bot
from twitch_bot.twitch_main import start_twitch_bot

async def main():
    load_dotenv()
    discord_token = os.getenv("DISCORD_TOKEN")
    twitch_token = "TWITCH_TOKEN"

    await start_discord_bot(discord_token),
    await start_twitch_bot(twitch_token)


    while True:
        await  asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
