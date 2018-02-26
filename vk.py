# coding=utf-8
# Project available at https://github.com/denexapp/advanced-status-vk
import urllib
from typing import Dict

import requests


class Vk:
    def __init__(self, access_token: str, api_version: str = '5.73'):
        self._access_token: str = access_token
        self._api_version: str = api_version

    def _make_vk_request(self, method: str, parameters: Dict[str, str]):
        parameters = dict(parameters)
        parameters['v'] = self._api_version
        parameters['access_token'] = self._access_token

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

    def set_status(self, text: str, group_id: str = None):
        parameters = {'text': text}
        if group_id:
            parameters['group_id'] = group_id
        self._make_vk_request('status.set', parameters)

    def get_status(self, user_id: str = None, group_id: str = None) -> str:
        parameters = {}
        if user_id:
            parameters['user_id'] = user_id
        if group_id:
            parameters['group_id'] = group_id
        response = self._make_vk_request('status.get', parameters)
        status = response['response']['text']
        return status
