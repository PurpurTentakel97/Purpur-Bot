from discord_bot.discord_chat import DiscordChat


discord_chat:DiscordChat

async def start_discord_bot(token:str) -> None:
    global discord_chat
    discord_chat = await DiscordChat.create(token)
