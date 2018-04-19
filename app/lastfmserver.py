# coding=utf-8
# Project available at https://github.com/denexapp/advanced-status-vk
import asyncio

import aiohttp
from aiohttp import web

from app import keys
from app.basedata import BaseData
from app.lastfm import LastFm
from app.lastfmdata import LastFmData


class LastFmServer:
    def __init__(self, last_fm_data: LastFmData, last_fm_session: LastFm,
                 session: aiohttp.ClientSession, loop: asyncio.AbstractEventLoop):
        self._data: LastFmData = last_fm_data
        self._last_fm: LastFm = last_fm_session
        self._session: aiohttp.ClientSession = session
        self._loop: asyncio.AbstractEventLoop = loop

    async def _get_last_fm_access_token(self, code: str):
        token, username = self._last_fm.get_last_fm_token(code)
        if self._data.is_user_exist(username):
            self._data.update_user(username, token=token)
        else:
            self._data.add_user(username, token=token)

    def _redirect_to_https(self, url):
        url.with_scheme('https')
        raise web.HTTPFound(url)

    async def _vk_auth_code_handler(self, request: web.Request) -> web.Response:
        if request.secure:
            pass
        elif not 'X-Forwarded-Proto' in request.headers:
            self._redirect_to_https(request.url)
        elif request.headers['X-Forwarded-Proto'] != 'https':
            self._redirect_to_https(request.url)
        url = '{}://{}{}'.format('https', request.host, request.path)
        query = request.query
        if 'token' in query:
            token = query['token']
            self._loop.create_task(self._get_last_fm_access_token(token, url))
            return web.Response(text="Отлично, а теперь вернись к боту")
        else:
            raise web.HTTPForbidden()

    async def run(self):
        app = web.Application()
        app.add_routes([web.get('/bot-api/last-fm-auth-callback', self._vk_auth_code_handler)])
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, '0.0.0.0', keys.server_port)
        await site.start()
