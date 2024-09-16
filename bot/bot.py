import discord
from discord.ext import commands

from help_cog import HelpCog
from music_cog import MusicCog


class MusicBot(commands.Bot):
    def __init__(self, command_prefix, activity, intents):
        super().__init__(command_prefix, activity=activity, intents=intents)
        self.remove_command('help')

    async def setup_hook(self):
        await self.add_cog(MusicCog(self))
        await self.add_cog(HelpCog(self))

    async def on_ready(self):
        print(f'Logged in as {self.user}')


bot = MusicBot(command_prefix=['/', '.'],
               activity=discord.Streaming(name=":3", url="https://www.youtube.com/watch?v=dQw4w9WgXcQ"),
               intents=discord.Intents.all())
