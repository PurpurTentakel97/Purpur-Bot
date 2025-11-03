import discord
from discord import Client

class DiscordClient(Client):
    def __init__(self,
                 *,
                 intents: discord.Intents):
        super().__init__(intents=intents)

    async def send_message(self, channel_id, message):
        channel = self.get_channel(channel_id)
        await channel.send(message)


    async def on_ready(self):
        print(f'{self.user} has connected to Discord!')

        channels = self.get_all_channels()
        for channel in channels:
            if channel.name == "announce":
                await self.send_message(channel.id, "||@everyone||\nHello World!")


    async def on_message(self, message):
        if message.author == self.user:
            return

        print(f'{message.author} said: {message.content}')

    async def on_error(self, event, *args, **kwargs):
        print(f'Error on {event}: {args} {kwargs}')
