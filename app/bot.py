import asyncio
from typing import Dict, Optional

import aiohttp
from yarl import URL
from asyncinit import asyncinit

from app.data import Data
from app.lastfm import LastFm
from app.vk import Vk
from app.dialogflow import Dialogflow


@asyncinit
class Bot:
    async def __init__(self, group_id: str,
                       group_access_token: str,
                       last_fm_api_key: str,
                       last_fm_shared_secret: str,
                       datastore_project_id: str,
                       datastore_credentials: str,
                       dialogflow_credentials: str,
                       loop: asyncio.AbstractEventLoop,
                       session: aiohttp.ClientSession):
        self._group_id: str = group_id
        self._group_access_token: str = group_access_token
        self._loop: asyncio.AbstractEventLoop = loop
        self._session: aiohttp.ClientSession = session
        self._data: Data = await Data(datastore_project_id, datastore_credentials, session)
        self._vk: Vk = Vk(self._group_id, self._group_access_token, self._loop, self._session)
        self._last_fm: LastFm = LastFm(last_fm_api_key, last_fm_shared_secret, self._loop, self._session)
        self._dialogflow: Dialogflow = Dialogflow(dialogflow_credentials, loop)

    def run_bot(self):
        self._loop.create_task(self._watch_vk_messages())
        self._loop.create_task(self._watch_last_fm_tracks())

    async def _watch_vk_messages(self):
        async for message in self._vk.get_message():
            self._loop.create_task(self._handle_message(message))

    async def _watch_last_fm_tracks(self):
        async for user_id, track in self._last_fm.get_new_now_playing():
            self._loop.create_task(self._set_status(user_id, track))

    async def _set_status(self, user_id: str, track: LastFm.Track):
        if track:
            status = "Слушает {} - {}"\
                .format(track.artist, track.name)
        else:
            status = "vk.me/advancedstatus"
        await self._vk.status_set_status(status, self._bot_data.get_user(user_id).vk_token)

    async def _handle_message(self, message: Dict):
        # description of message could be find here: https://vk.com/dev/objects/message
        user_id: int = message['user_id']
        input_message_text = message['body']
        # if not self._bot_data.is_user_exist(user_id):
        #     self._bot_data.add_user(user_id)
        dialogflow_response = await self._dialogflow.detect_intent(input_message_text, user_id)
        await self._vk.messages_send_message(str(user_id), dialogflow_response)

    def _extract_token(self, url: str, user_id: str) -> Optional[str]:
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
