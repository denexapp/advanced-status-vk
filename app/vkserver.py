# coding=utf-8
# Project available at https://github.com/denexapp/advanced-status-vk
import asyncio

import aiohttp
from aiohttp import web

from app import keys
from app.basedata import BaseData


class Server:
    def __init__(self, data: BaseData, session: aiohttp.ClientSession, loop: asyncio.AbstractEventLoop):
        self._data = data  # type: BaseData
        self._session = session  # type: aiohttp.ClientSession
        self._loop = loop

    async def _get_vk_access_token(self, code: str, redirect_uri: str):
        parameters = {
            'client_id': keys.vk_app_client_id,
            'client_secret': keys.vk_app_client_secret,
            'redirect_uri': redirect_uri,
            'code': code
        }
        url = 'https://oauth.vk.com/access_token'
        async with self._session.get(url, params=parameters) as response:
            result = await response.json()
            if 'access_token' in result:
                user_id = str(result['user_id'])
                access_token = result['access_token']
                if self._data.does_user_exist(user_id):
                    self._data.add_vk_access_token(user_id, access_token)
                else:
                    print('Can\'t find user: {}'.format(user_id))
            else:
                print('Can\'t find access token:')
                print(redirect_uri)
                print(code)
                print(result)

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
        if 'code' in query:
            code = query['code']
            self._loop.create_task(self._get_vk_access_token(code, url))
            return web.Response(text="Отлично, а теперь вернись к боту")
        elif 'error' in query and 'error_description':
            return web.Response(text="Ошибка! Вот, что говорит ВК: {}: {}"
                                .format(query['error'], query['error_description']))
        else:
            raise web.HTTPForbidden()

    async def run(self):
        app = web.Application()
        app.add_routes([web.get('/bot-api/vk-auth-callback', self._vk_auth_code_handler)])
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, '0.0.0.0', keys.server_port)
        await site.start()
