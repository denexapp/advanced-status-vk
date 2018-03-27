# coding=utf-8
# Project available at https://github.com/denexapp/advanced-status-vk
from typing import List, Dict, Tuple
import urllib
import hashlib
import xml.dom.minidom as minidom

import requests


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

    def __init__(self, username: str, password: str, api_key: str, shared_secret: str):
        self._api_key: str = api_key
        self._shared_secret: str = shared_secret
        self._session_key: str = self._get_last_fm_token(username, password)

    def _make_last_fm_request_signature(self, request_parameters: _RequestParameters) -> str:
        signing_string = ""
        for key, value in request_parameters.get_sorted_parameters():
            signing_string += key + value
        signing_string += self._shared_secret
        return hashlib.md5(signing_string.encode()).hexdigest()

    def _make_last_fm_request(self, parameters: _RequestParameters,
                              session_key_request: bool = False, requires_signing: bool = False):
        parameters.add_parameter('api_key', self._api_key)
        if not session_key_request:
            parameters.add_parameter('sk', self._session_key)
            # When it requests for session key, no format needed
            parameters.add_parameter('format', 'json')
        if requires_signing or session_key_request:
            signature = self._make_last_fm_request_signature(parameters)
            parameters.add_parameter('api_sig', signature)

        url = "https://ws.audioscrobbler.com/2.0/?"
        for name, value in parameters.get_parameters():
            url += '{}={}&'.format(urllib.parse.quote(name), urllib.parse.quote(value))
        url = url[:-1]

        if session_key_request:
            response = requests.post(url)
        else:
            response = requests.get(url)
        return response.json() if not session_key_request else minidom.parseString(response.content.decode())

    def _get_last_fm_token(self, username: str, password: str) -> str:
        parameters = self._RequestParameters('auth.getMobileSession')\
            .add_parameter('username', username)\
            .add_parameter('password', password)
        response = self._make_last_fm_request(parameters, session_key_request=True)
        token = response.getElementsByTagName('key')[0].childNodes[0].data
        return token

    def get_last_fm_now_playing(self, username: str) -> Track:
        parameters = self._RequestParameters('user.getRecentTracks')\
            .add_parameter('limit', '1')\
            .add_parameter('user', username)
        response = self._make_last_fm_request(parameters)
        track = response["recenttracks"]['track'][0]
        now_playing = False
        if '@attr' in track:
            if 'nowplaying' in track['@attr']:
                now_playing = track['@attr']['nowplaying'] = 'true'
        if not now_playing:
            return None
        return self.Track(track['name'], track['artist']['#text'])
