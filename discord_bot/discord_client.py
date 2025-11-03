import discord
from discord import Client

class DiscordClient(Client):
    def __init__(self,
                 *,
                 intents: discord.Intents):
        super().__init__(intents=intents)


    async def on_ready(self):
        print(f'{self.user} has connected to Discord!')


    async def on_message(self, message):
        if message.author == self.user:
            return

        print(f'{message.author} said: {message.content}')
