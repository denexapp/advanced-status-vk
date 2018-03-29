# coding=utf-8
# Project available at https://github.com/denexapp/advanced-status-vk
from typing import Dict, Iterable


class Data:
    class User:
        def __init__(self, user_id: str):
            self.user_id = user_id  # type: str
            self.vk_token = None  # type: str

    def __init__(self):
        self._users = dict()  # type: Dict[str, Data.User]

    def add_user(self, user_id: str):
        self._users[user_id] = Data.User(user_id)

    def add_vk_access_token(self, user_id: str, token: str):
        self._users[user_id].vk_token = token

    def does_user_exist(self, user_id: str):
        return user_id in self._users

    def get_users(self) -> Iterable['Data.User']:
        return self._users.values[:]

    def get_user(self, user_id: str) -> 'Data.User':
        return self._users[user_id]