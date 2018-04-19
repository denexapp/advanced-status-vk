# coding=utf-8
# Project available at https://github.com/denexapp/advanced-status-vk
import asyncio
from typing import Dict, Tuple, AsyncIterable

import aiohttp

from app.basedata import BaseData
from app.ratelimiter import RateLimiter


class Vk:
    def __init__(self, group_id: str, group_access_token: str, loop: asyncio.AbstractEventLoop,
                 session: aiohttp.ClientSession, api_version: str = '5.74'):
        self._group_id = group_id  # type: str
        self._group_access_token = group_access_token  # type: str
        self._data = BaseData()  # type: BaseData
        self._api_version: str = api_version
        self._session: aiohttp.ClientSession = session
        self._loop = loop  # type: asyncio.AbstractEventLoop
        self._rate_limiter = RateLimiter(loop)  # type: RateLimiter

    async def _make_vk_request(self, url: str, parameters: Dict[str, str]):
        async with self._session.get(url, params=parameters) as response:
            content = await response.json()
            if 'error' in content:
                raise Exception(content)
            else:
                return content

    async def _prepare_vk_request(self, method: str, parameters: Dict[str, str], access_token: str = None,
                                  group: bool = True):
        parameters = dict(parameters)
        parameters['v'] = self._api_version
        parameters['access_token'] = access_token if access_token else self._group_access_token
        url = 'https://api.vk.com/method/{}'.format(method)
        delay = 0.055 if group else 0.350
        await self._rate_limiter.wait_before_request(access_token, delay)
        return await self._make_vk_request(url, parameters)

    async def get_message(self) -> AsyncIterable:
        await self.groups_set_long_poll_settings(self._group_id, enabled=True, message_new=True)
        key, server, timestamp = await self.groups_get_long_poll_server(self._group_id)
        while True:
            parameters = {'act': 'a_check', 'key': key, 'ts': timestamp, 'wait': '15'}
            try:
                async with self._session.get(server, params=parameters) as response:
                    content = await response.json()
            except aiohttp.ServerDisconnectedError:
                key, server, timestamp = await self.groups_get_long_poll_server(self._group_id)
                continue
            if 'failed' in content:
                error_code = content['failed']
                if error_code == 1:
                    timestamp = content['ts']
                elif error_code == 2:
                    key, _, _ = await self.groups_get_long_poll_server(self._group_id)
                elif error_code == 2:
                    key, _, ts = await self.groups_get_long_poll_server(self._group_id)
            else:
                timestamp = content['ts']
                updates = content['updates']
                for event in updates:
                    if event['type'] == 'message_new':
                        yield event['object']

    async def messages_send_message(self, user_id: str, message: str):
        parameters = {'user_id': user_id, 'message': message}
        await self._prepare_vk_request('messages.send', parameters)

    async def groups_get_long_poll_server(self, group_id: str) -> Tuple[str, str, str]:
        parameters = {'group_id': group_id}
        response = await self._prepare_vk_request('groups.getLongPollServer', parameters)
        key = response['response']['key']
        server = response['response']['server']
        timestamp = response['response']['ts']
        return key, server, timestamp

    async def groups_set_long_poll_settings(self, group_id: str, enabled: bool = None, message_new: bool = None):
        parameters = {'group_id': group_id}
        if enabled is not None:
            parameters['enabled'] = '1' if enabled else '0'
        if message_new is not None:
            parameters['message_new'] = '1' if message_new else '0'
        await self._prepare_vk_request('groups.setLongPollSettings', parameters)

    async def status_set_status(self, text: str, token: str = None, group_id: str = None):
        parameters = {'text': text}
        if group_id:
            parameters['group_id'] = group_id
        await self._prepare_vk_request('status.set', parameters, access_token=token)

    async def status_get_status(self, token: str = None, user_id: str = None, group_id: str = None) -> Tuple[str, bool]:
        parameters = {}
        if user_id:
            parameters['user_id'] = user_id
        if group_id:
            parameters['group_id'] = group_id
        response = await self._prepare_vk_request('status.get', parameters, access_token=token)
        status = response['response']['text']
        audio = 'audio' in response['response']
        return status, audio

    # async def secure_check_token(self, token: str, ip: str) -> Dict:
    #     parameters = {'token': token, 'ip': ip}
    #     response = await self._prepare_vk_request('secure.checkToken', parameters, access_token=self._client_secret)
    #     return response['response']
