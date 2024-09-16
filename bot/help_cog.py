from discord.ext import commands

from bot.config import INACTIVITY_TIMEOUT, MAX_TRACKS_IN_PLAYLIST


class HelpCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help", aliases=["р", "рудз"])
    async def help(self, ctx):
        await ctx.send(f"""
```
Особенности бота:
Бот ставит первые {MAX_TRACKS_IN_PLAYLIST} треков из плейлиста
Бот выходит из голосового канала после {int(INACTIVITY_TIMEOUT.total_seconds() // 60)} минут неактивности

Команды бота:
/play <ключевые слова для поиска || ссылка на YouTube/Yandex> - воспроизведение трека/плейлиста
/skip - пропускает текущую песню
/skipplaylist - пропускает треки текущего плейлиста из очереди
/pause - приостанавливает воспроизведение песни или возобновляет его, если уже на паузе
/queue|list - отображает текущую очередь треков
/clear - очищает текущую очередь
/leave - отключает бота от голосового канала
```
""")
