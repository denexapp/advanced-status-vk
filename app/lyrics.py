import asyncio

import aiohttp
import bs4
import lyricsgenius

g = lyricsgenius.Genius('ZGFwcECgWteA7lFx5rYlSRmdgO6daYHywwo0E4u_A1TqE3XQimBt03aN-lticsyh',
                        '3mUn9J2GiU8qmgQbGVubqfpG8b_1jHUkmiK7YSEuz9OuKC5iayTGfGg_vXwCwXklGLwaaQ1SA3k3ClhIB7mmVw',
                        'xPMi1TJx2LiJ33GdoMGx-qsHQuRmRGgfLUOgExKvB9TNzPZEYmhqmAWImEIGh6n1')
r = g.search_song('плот', 'мы', take_first_result=True)
print(r.lyrics)

# class Lyrics:
#     def __init__(self, session: aiohttp.ClientSession, loop: asyncio.AbstractEventLoop):
#         self._session: aiohttp.ClientSession = session
#         self._loop: asyncio.AbstractEventLoop = loop
#
#     def create_url(self, artist: str, song: str):
#         return 'https://lyrics.wikia.com/wiki/{}:{}' \
#             .format(artist=urlize(artist),
#             song=urlize(song)))
#
#     async def find_lyrics(self):
#         url = create_url(artist, song)
#         response = _requests.get(url, timeout=timeout)
#         soup = _BeautifulSoup(response.content, "html.parser")
#         lyricboxes = soup.findAll('div', {'class': 'lyricbox'})
#
#         if not lyricboxes:
#             raise LyricsNotFound('Cannot download lyrics')
#
#         for lyricbox in lyricboxes:
#             for br in lyricbox.findAll('br'):
#                 br.replace_with(linesep)
