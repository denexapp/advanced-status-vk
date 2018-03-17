# coding=utf-8
# Project available at https://github.com/denexapp/advanced-status-vk
import urllib
from typing import Dict, Tuple

import requests


class Vk:
    def __init__(self, group_id: str, group_access_token: str, api_version: str = '5.73'):
        self._group_id = group_id
        self._group_access_token = group_access_token
        self._api_version = api_version

    def _make_vk_request(self, method: str, parameters: Dict[str, str], access_token: str = None):
        parameters = dict(parameters)
        parameters['v'] = self._api_version
        parameters['access_token'] = access_token if access_token else self._group_access_token

        url = 'https://api.vk.com/method/{}?'.format(method)
        for name, value in parameters.items():
            url += '{}={}&'.format(urllib.parse.quote(name), urllib.parse.quote(value))
        url = url[:-1]

        response = requests.get(url)
        content = response.json()
        if "error" in content:
            raise Exception(content)
        else:
            return content

    def _handle_message(self, message: Dict):
        # description of message could be find there: https://vk.com/dev/objects/message
        user_id = str(message['user_id'])
        body = message['body']
        message = "Ты написал: {}".format(body)
        self.messages_send_message(user_id, message)

    def _run_long_poll(self):
        self.groups_set_long_poll_settings(self._group_id, enabled=True, message_new=True)
        key, server, timestamp = self.groups_get_long_poll_server(self._group_id)
        while True:
            url = '{}?act=a_check&key={}&ts={}&wait=25'.format(server, key, timestamp)
            response = requests.get(url)
            content = response.json()
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
                        self._handle_message(event['object'])

    def start_bot(self):
        self._run_long_poll()

    def messages_send_message(self, user_id: str, message: str):
        parameters = {'user_id': user_id, 'message': message}
        self._make_vk_request('messages.send', parameters)

    def groups_get_long_poll_server(self, group_id: str) -> Tuple[str, str, str]:
        parameters = {'group_id': group_id}
        response = self._make_vk_request('groups.getLongPollServer', parameters)
        key = response['response']['key']
        server = response['response']['server']
        timestamp = response['response']['ts']
        print(response)
        print(server)
        return key, server, timestamp

    def groups_set_long_poll_settings(self, group_id: str, enabled: bool = None, message_new: bool = None):
        parameters = {'group_id': group_id}
        if enabled is not None:
            parameters['enabled'] = '1' if enabled else '0'
        if message_new is not None:
            parameters['message_new'] = '1' if message_new else '0'
        self._make_vk_request('groups.setLongPollSettings', parameters)

    def status_set_status(self, text: str, group_id: str = None):
        parameters = {'text': text}
        if group_id:
            parameters['group_id'] = group_id
        self._make_vk_request('status.set', parameters)

    def status_get_status(self, user_id: str = None, group_id: str = None) -> str:
        parameters = {}
        if user_id:
            parameters['user_id'] = user_id
        if group_id:
            parameters['group_id'] = group_id
        response = self._make_vk_request('status.get', parameters)
        status = response['response']['text']
        return status
