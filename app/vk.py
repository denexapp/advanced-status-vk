# coding=utf-8
# Project available at https://github.com/denexapp/advanced-status-vk
import asyncio
from typing import Dict, Tuple

import aiohttp

from app import keys
from app.data import Data
from app.ratelimiter import RateLimiter


class Vk:
    def __init__(self, group_id: str, group_access_token: str, loop: asyncio.AbstractEventLoop,
                 session: aiohttp.ClientSession, data: Data, api_version: str = '5.73'):
        self._group_id = group_id  # type: str
        self._group_access_token = group_access_token  # type: str
        self._data = data  # type: Data
        self._api_version = api_version  # type: str
        self._session = session  # type: aiohttp.ClientSession
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

    async def _handle_message(self, message: Dict):
        # description of message could be find there: https://vk.com/dev/objects/message
        user_id = str(message['user_id'])
        body = message['body']
        if not self._data.does_user_exist(user_id):
            self._data.add_user(user_id)
        user = self._data.get_user(user_id)
        if user.vk_token is None:
            message = 'Для начала тебя нужно авторизовать. Перейди по ссылке: ' + keys.vk_auth_link
            await self.messages_send_message(user_id, message)
        else:
            message = 'Устанавливаю статус в: {}'.format(body)
            await self.messages_send_message(user_id, message)
            await self.status_set_status(body, user.vk_token)
            message = 'Готово.'
            await self.messages_send_message(user_id, message)

    async def run_long_poll(self):
        await self.groups_set_long_poll_settings(self._group_id, enabled=True, message_new=True)
        key, server, timestamp = await self.groups_get_long_poll_server(self._group_id)
        while True:
            parameters = {'act': 'a_check', 'key': key, 'ts': timestamp, 'wait': '15'}
            async with self._session.get(server, params=parameters) as response:
                content = await response.json()
            if 'failed' in content:
                error_code = content['failed']
                if error_code == 1:
                    timestamp = content['ts']
                elif error_code == 2:
                    key, _, _ = self.groups_get_long_poll_server(self._group_id)
                elif error_code == 2:
                    key, _, ts = self.groups_get_long_poll_server(self._group_id)
            else:
                timestamp = content['ts']
                updates = content['updates']
                for event in updates:
                    if event['type'] == 'message_new':
                        self._loop.create_task(self._handle_message(event['object']))

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

    async def status_get_status(self, user_id: str = None, group_id: str = None) -> str:
        parameters = {}
        if user_id:
            parameters['user_id'] = user_id
        if group_id:
            parameters['group_id'] = group_id
        response = await self._prepare_vk_request('status.get', parameters)
        status = response['response']['text']
        return status
