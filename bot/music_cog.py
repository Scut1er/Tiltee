from discord.ext import commands

from player import Player
from discord.ext.commands import CommandOnCooldown


class MusicCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.players = {}

    def get_player(self, ctx):
        if ctx.guild.id not in self.players:
            self.players[ctx.guild.id] = Player(ctx)
        else:
            self.players[ctx.guild.id].update_ctx(ctx)
        return self.players[ctx.guild.id]

    @commands.command(name="play", aliases=["PLAY", "Play", "p", "з", "здфн"])
    @commands.cooldown(1, 1, commands.BucketType.user)
    async def play(self, ctx, *, query=None):
        if not query:
            return await ctx.send(
                "```❌ Неправильное использование. Правильный синтаксис: /play <ключевые слова или URL>```")
        player = self.get_player(ctx)
        await player.handle_query(query)

    @commands.command(name="queue", aliases=["QUEUE", "LIST", "list", "l", "дшые", "д" "q", "й", "йгугу"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def queue(self, ctx):
        player = self.get_player(ctx)
        await player.show_queue()

    @commands.command(name="clear", aliases=["CLEAR", "c", "сдуфк"])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def clear(self, ctx):
        player = self.get_player(ctx)
        await player.clear_queue()

    @commands.command(name="skip", aliases=["SKIP", "s", "ы", "ылшз"])
    @commands.cooldown(1, 1, commands.BucketType.user)
    async def skip(self, ctx):
        player = self.get_player(ctx)
        await player.skip()

    @commands.command(name="skip_playlist",
                      aliases=["SKIP_P", "skip_p", "skipplaylist", "ылшз_з", "ылшз_здфндшые", "ылшзздфндшые"])
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def skip_playlist(self, ctx):
        player = self.get_player(ctx)
        await player.skip_playlist()

    @commands.command(name="pause", aliases=["PAUSE", "resume", "r", "к", "зфгыу"])
    @commands.cooldown(1, 1, commands.BucketType.user)
    async def pause(self, ctx):
        player = self.get_player(ctx)
        await player.pause()

    @commands.command(name="kick", aliases=["DISCONNECT", "KICK", "disconnect", "leave", "dc", "дуфму", "лшсл"])
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def kick(self, ctx):
        player = self.get_player(ctx)
        await player.disconnect()

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, CommandOnCooldown):
            await ctx.send(f"⏳ Подождите {error.retry_after:.2f} сек. перед повторным использованием команды.")
