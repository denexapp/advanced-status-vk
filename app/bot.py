import asyncio
from typing import Dict

import aiohttp
from yarl import URL

from app.botdata import BotData
from app.lastfm import LastFm
from app.lastfmdata import LastFmData
from app.vk import Vk


class Bot:
    def __init__(self, group_id: str, group_access_token: str, last_fm_api_key: str, last_fm_shared_secret: str,
                 loop: asyncio.AbstractEventLoop, session: aiohttp.ClientSession):
        self._group_id: str = group_id
        self._group_access_token: str = group_access_token
        self._loop: asyncio.AbstractEventLoop = loop
        self._session: aiohttp.ClientSession = session

        self._bot_data: BotData = BotData()
        self._last_fm_data: LastFmData = LastFmData()

        self._vk: Vk = Vk(self._group_id, self._group_access_token, self._loop, self._session)
        self._last_fm: LastFm = LastFm(last_fm_api_key, last_fm_shared_secret, self._last_fm_data,
                                       self._loop, self._session)

    async def run_bot(self):
        self._loop.create_task(self._watch_vk_messages())
        self._loop.create_task(self._watch_last_fm_tracks())

    async def _watch_vk_messages(self):
        async for message in self._vk.get_message():
            self._loop.create_task(self._handle_message(message))

    async def _watch_last_fm_tracks(self):
        print(0)
        async for user_ids, track in self._last_fm.get_new_now_playing():
            print(1)
            for user_id in user_ids:
                self._loop.create_task(self._set_status(user_id, track))

    async def _set_status(self, user_id: str, track: LastFm.Track):
        if track:
            status = "Слушает {} - {}, vk.me/advancedstatus"\
                .format(track.name, track.artist)
        else:
            status = "vk.me/advancedstatus"
        await self._vk.status_set_status(status, self._bot_data.get_user(user_id).vk_token)

    async def _handle_message(self, message: Dict):
        # description of message could be find there: https://vk.com/dev/objects/message
        user_id: str = str(message['user_id'])
        body: str = message['body']
        if not self._bot_data.is_user_exist(user_id):
            self._bot_data.add_user(user_id)
        user = self._bot_data.get_user(user_id)
        if not user.vk_token:
            token = self._extract_token(body, user_id)
            if token:
                self._bot_data.update_user(user_id, token)
                message = 'Отлично, теперь ты можешь подключить аккаунт Last.Fm командой:\n' \
                          'setlastfm твой_ник'
                await self._vk.messages_send_message(user_id, message)
            else:
                message = 'Для начала тебя нужно авторизовать. ' \
                          'Перейди по ссылке и пришли мне ссылку из адресной строки: \n' \
                          'https://oauth.vk.com/authorize?client_id=6386667&' \
                          'redirect_uri=https://oauth.vk.com/blank.html&' \
                          'scope=offline,status&response_type=token&v=5.74'
                await self._vk.messages_send_message(user_id, message)

        elif body.startswith('setlastfm '):
            #todo
            last_fm_id = body[10:]
            self._last_fm_data.add_user(last_fm_id, user_id)
            message = 'Добавил {} для пользователя {}'.format(last_fm_id, user_id)
            await self._vk.messages_send_message(user_id, message)
        elif body.startswith('unsetlastfm '):
            pass
        elif body.startswith('forget'):
            pass
        else:
            message = 'Эта команда не поддерживается, потому что мой' \
                      'разработчик ленивая жопа.'
            await self._vk.messages_send_message(user_id, message)

    def _extract_token(self, url: str, user_id: str) -> str:
        url = URL(url)
        if url.scheme != 'https':
            return None
        elif url.host is None:
            return None
        elif url.host != 'oauth.vk.com':
            return None
        elif url.path != '/blank.html':
            return None
        elif url.fragment == '':
            return None
        elif url.query_string != '':
            return None
        query = url.with_query(url.fragment).query
        if 'access_token' not in query:
            return None
        elif query['access_token'] == '':
            return None
        elif 'expires_in' not in query:
            return None
        elif query['expires_in'] != '0':
            return None
        elif 'user_id' not in query:
            return None
        elif query['user_id'] != user_id:
            return None
        return query['access_token']

