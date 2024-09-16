import asyncio
from datetime import datetime, timezone

import validators
from asyncio import sleep
import discord

from bot.config import FFMPEG_OPT, INACTIVITY_TIMEOUT
from searcher import search_track, get_first_tracks_from_playlist, search_playlist


def update_last_activity(method=None):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            self = args[0]
            if isinstance(self, Player):
                self.last_activity = datetime.now(timezone.utc)
            return await func(*args, **kwargs)

        if method:
            return wrapper
        return wrapper()

    if callable(method):
        return decorator(method)
    return decorator


class Player:
    """
    Класс Player отвечает за управление воспроизведением музыки в голосовом канале Discord.

    Атрибуты:
    - ctx: Контекст, в котором используется Player.
    - bot: Экземпляр бота.
    - voice_client: Клиент голосового канала Discord.
    - is_playing: Логический индикатор того, воспроизводится ли трек в данный момент.
    - current_track: Текущий воспроизводимый трек.
    - current_playlist: Текущий воспроизводимый плейлист.
    - queue: Очередь треков для воспроизведения.
    - playlist_loading: Логический индикатор того, загружается ли плейлист в данный момент.
    - last_activity: Время последней активности в формате UTC.
    - inactivity_task: Задача, отслеживающая бездействие и отключение бота.
    """

    def __init__(self, ctx):
        self.ctx = ctx
        self.bot = ctx.bot
        self.voice_client = None
        self.is_playing = False
        self.current_track = None
        self.playlists = []
        self.queue = []
        self.playlist_loading = False
        self.last_activity = datetime.now(timezone.utc)
        self.inactivity_task = asyncio.create_task(self.check_inactivity())

    def update_ctx(self, ctx):
        """Обновляет текущий контекст."""
        self.ctx = ctx

    @update_last_activity
    async def handle_query(self, query):
        """
        Обрабатывает запрос и определяет, является ли он треком или плейлистом,
        вызывая соответствующую функцию.

        Parameters:
        - query: Запрос для обработки.
        """
        if self.playlist_loading:
            return await self.ctx.send(
                "```⏳ Команда недоступна во время загрузки плейлиста. Пожалуйста, подождите...```")
        if validators.url(query) and ('?list=' in query or '/playlists/' in query):
            return await self.add_playlist_to_queue(query)
        return await self.add_track_to_queue(query)

    async def check_inactivity(self):
        while True:
            await sleep(60)  # Проверяем раз в минуту
            if self.voice_client and self.voice_client.is_connected() and not self.voice_client.is_playing():
                if datetime.now(timezone.utc) - self.last_activity > INACTIVITY_TIMEOUT:
                    await self.voice_client.disconnect()
                    await self.ctx.send("```💤 Бот отключен из-за неактивности.```")
                    break

    async def connect(self):
        """
        Подключает бота к голосовому каналу пользователя, вызвавшего команду.

        Returns:
        - True, если подключение было успешным, False в противном случае.
        """
        try:
            voice_channel = self.ctx.author.voice.channel
        except AttributeError:
            await self.ctx.send("```❌ Вы не находитесь в голосовом канале!```")
            return False
        if self.voice_client and self.voice_client.is_connected():
            if self.voice_client.channel != voice_channel:
                await self.voice_client.move_to(voice_channel)
            return True
        self.voice_client = await voice_channel.connect(self_deaf=True)
        return True

    @update_last_activity
    async def disconnect(self):
        """Отключает бота от голосового канала и очищает очередь."""
        if self.voice_client and self.voice_client.is_connected():
            await self.clear_queue()
            await self.voice_client.disconnect()
            await self.ctx.send("```💔 Отключено```")

    @update_last_activity
    async def add_track_to_queue(self, query):
        """
        Добавляет трек в очередь.

        Parameters:
        - query: Запрос для поиска или URL трека.
        """
        if await self.connect():
            track = await search_track(self, query)
            if not track:
                return await self.ctx.send("```🔍 По вашему запросу ничего не найдено.```")
            self.queue.append(track)
            await self.ctx.send(f'```📥 Добавлено {track.title}```')
            if not self.voice_client.is_playing():
                await self.play_track()

    @update_last_activity
    async def add_playlist_to_queue(self, query):
        """
        Добавляет плейлист в очередь.

        Parameters:
        - query: URL плейлиста.
        """
        if await self.connect():
            upload_text = await self.ctx.send("```♻️ Добавление плейлиста в очередь. Пожалуйста, подождите...```")
            self.playlist_loading = True
            first_tracks = await get_first_tracks_from_playlist(self, query)
            if first_tracks:
                self.queue.extend(first_tracks)
                await self.play_track()
            playlist = await search_playlist(self, query)
            self.playlist_loading = False
            await upload_text.delete()
            if not playlist:
                return await self.ctx.send("```❌ Неверный или пустой плейлист.```")
            self.queue.extend(playlist[len(first_tracks):])
            self.playlists.append(query)
            await self.ctx.send(f'```📥 Добавлено {len(playlist) - 1} треков из плейлиста в очередь.```')

            if not self.voice_client.is_playing():
                await self.play_track()

    @update_last_activity
    async def play_track(self):
        """Воспроизводит следующий трек в очереди."""
        if not self.voice_client or not self.voice_client.is_connected() or self.voice_client.is_playing():
            return
        self.current_track = self.queue.pop(0)
        self.voice_client.play(
            discord.FFmpegPCMAudio(self.current_track.source, **FFMPEG_OPT),
            after=lambda e: self.bot.loop.create_task(self.play_track()) if self.queue else None)

    @update_last_activity
    async def show_queue(self):
        """Отображает текущую очередь."""
        if self.playlist_loading:
            return await self.ctx.send(
                "```⏳ Команда недоступна во время загрузки плейлиста. Пожалуйста, подождите...```")
        if not self.queue:
            await self.ctx.send("```📭 Очередь пуста.```")
        else:
            text_queue = [f"{i + 1}) {str(track)}" for i, track in enumerate(self.queue)]
            chunks = [text_queue[i:i + 30] for i in range(0, len(text_queue), 30)]

            for i, chunk in enumerate(chunks):
                chunk_text = "\n".join(chunk)
                if i == 0:
                    await self.ctx.send(f"**Текущая очередь:**\n```{chunk_text}```")
                else:
                    await self.ctx.send(f"```{chunk_text}```")

    @update_last_activity
    async def clear_queue(self):
        """Очищает текущую очередь."""
        if self.playlist_loading:
            return await self.ctx.send(
                "```⏳ Команда недоступна во время загрузки плейлиста. Пожалуйста, подождите...```")
        if not self.queue:
            await self.ctx.send("```📭 Очередь пуста.```")
        else:
            self.queue.clear()
            await self.ctx.send("```✨ Очередь очищена.```")

    @update_last_activity
    async def skip(self):
        """Пропускает текущий воспроизводимый трек."""
        if not (self.voice_client and self.voice_client.is_playing()):
            return
        if self.playlist_loading:
            return await self.ctx.send(
                "```⏳ Команда недоступна во время загрузки плейлиста. Пожалуйста, подождите...```")
        self.voice_client.stop()
        await self.ctx.send('```⏭️ Пропущено```')
        if self.queue and not self.voice_client.is_playing():
            await self.play_track()

    @update_last_activity
    async def skip_playlist(self):
        """Пропускает текущий воспроизводимый плейлист."""
        if not (self.voice_client and self.voice_client.is_playing()):
            return
        if self.playlist_loading:
            return await self.ctx.send(
                "```⏳ Команда недоступна во время загрузки плейлиста. Пожалуйста, подождите...```")
        if not self.playlists:
            await self.ctx.send("```⚠️ Текущий плейлист отсутствует.```")
            return
        current_playlist = self.playlists.pop(0)
        self.queue = [track for track in self.queue if track.playlist != current_playlist]
        await self.ctx.send(f"```⏭️ Пропущен текущий плейлист.```")

    @update_last_activity
    async def pause(self):
        """Приостанавливает или возобновляет воспроизведение текущего трека."""
        if self.voice_client.is_playing():
            self.voice_client.pause()
            await self.ctx.send('```⏸️ Пауза```')
        elif self.voice_client.is_paused():
            self.voice_client.resume()
            await self.ctx.send("```🔊 Возобновлено```")
