# coding=utf-8
# Project available at https://github.com/denexapp/advanced-status-vk
import asyncio
from typing import List, Dict, Tuple, AsyncIterable
import hashlib
import xml.dom.minidom as minidom

import aiohttp

from app.ratelimiter import RateLimiter


class LastFm:
    class _RequestParameters:
        def __init__(self, method: str):
            self._parameters: Dict = {'method': method}

        def add_parameter(self, name: str, value: str) -> 'LastFm._RequestParameters':
            self._parameters[name] = value
            return self

        def get_sorted_parameters(self) -> List[Tuple[str, str]]:
            return sorted(self._parameters.items(), key=lambda x: x[0])

        def get_parameters(self) -> List[Tuple[str, str]]:
            return list(self._parameters.items())

    class Track:
        def __init__(self, name: str, artist: str):
            self.name: str = name
            self.artist: str = artist

    def __init__(self, api_key: str, shared_secret: str, loop: asyncio.AbstractEventLoop,
                 session: aiohttp.ClientSession):
        self._api_key: str = api_key
        self._shared_secret: str = shared_secret
        self._session: aiohttp.ClientSession = session
        self._loop: asyncio.AbstractEventLoop = loop
        self._rate_limiter: RateLimiter = RateLimiter(loop)
        self._rate = 0.2
        self._pool_rate = 10

    def _make_last_fm_request_signature(self, request_parameters: _RequestParameters) -> str:
        signing_string = ""
        for key, value in request_parameters.get_sorted_parameters():
            signing_string += key + value
        signing_string += self._shared_secret
        return hashlib.md5(signing_string.encode()).hexdigest()

    async def _make_last_fm_request(self, parameters: _RequestParameters, session_key_request: bool = False,
                                    requires_signing: bool = False, session_key: str = None):
        parameters.add_parameter('api_key', self._api_key)
        if not session_key_request:
            # When it requests for session key, no format needed
            parameters.add_parameter('format', 'json')
        if session_key:
            parameters.add_parameter('sk', session_key)
        if requires_signing or session_key_request:
            signature = self._make_last_fm_request_signature(parameters)
            parameters.add_parameter('api_sig', signature)
        await self._rate_limiter.wait_before_request('request', self._rate)
        url = "https://ws.audioscrobbler.com/2.0/?"
        if session_key_request:
            async with self._session.post(url, params=parameters.get_sorted_parameters()) as response:
                xml = await response.text(encoding='utf8')
                result = minidom.parseString(xml)
        else:
            async with await self._session.get(url, params=parameters.get_sorted_parameters()) as response:
                result = await response.json()
        return result

    async def get_token(self, code: str) -> Tuple[str, str]:
        parameters = self._RequestParameters('auth.getSession') \
            .add_parameter('token ', code)
        response = await self._make_last_fm_request(parameters, session_key_request=True)
        token = response.getElementsByTagName('key')[0].childNodes[0].data
        username = response.getElementsByTagName('key')[0].childNodes[0].data
        return token, username

    async def get_now_playing(self, username: str) -> Track:
        parameters = self._RequestParameters('user.getRecentTracks') \
            .add_parameter('limit', '1') \
            .add_parameter('user', username)
        response = await self._make_last_fm_request(parameters)
        track = response["recenttracks"]['track'][0]
        now_playing = False
        if '@attr' in track:
            if 'nowplaying' in track['@attr']:
                now_playing = track['@attr']['nowplaying'] = 'true'
        if not now_playing:
            return None
        return self.Track(track['name'], track['artist']['#text'])

    async def _get_now_playing_with_user(self, user: LastFmData.LastFmUser) -> Tuple[LastFmData.LastFmUser, Track]:
        return user, await self.get_now_playing(user.user_id)

    async def get_new_now_playing(self) -> AsyncIterable:
        while True:
            await self._rate_limiter.wait_before_request('requests', self._pool_rate)
            tasks = [self._get_now_playing_with_user(user) for user in self._data.get_users()]
            for task in asyncio.as_completed(tasks, loop=self._loop):
                user, track = await task
                if track:
                    if user.track_name != track.name or user.track_artist != track.artist:
                        self._data.update_user(user.user_id, track_name=track.name, track_artist=track.artist)
                        for vk_user in user.vk_user_ids:
                            yield vk_user, track
                else:
                    user_track_exist = user.track_name is not None
                    user_artist_exist = user.track_artist is not None
                    if user_artist_exist or user_track_exist:
                        self._data.none_user(user.user_id,
                                             track_name=user_track_exist,
                                             track_artist=user_artist_exist)
                        for vk_user in user.vk_user_ids:
                            yield vk_user, None
