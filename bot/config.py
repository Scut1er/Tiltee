from datetime import timedelta

TRACKS_FOR_WAITING = 1
MAX_TRACKS_IN_PLAYLIST = 100
USE_LOGGING = True
INACTIVITY_TIMEOUT = timedelta(minutes=15)
FFMPEG_OPT = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
              'options': '-vn -loglevel panic',
              'stderr': None}
YDL_OPT = {'format': "bestaudio/best",
           'source_address': '0.0.0.0',
           'noplaylist': False,
           'cookiefile': 'cookies.txt',
           'ignoreerrors': True,
           'playlistend': MAX_TRACKS_IN_PLAYLIST}
