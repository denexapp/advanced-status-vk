# coding=utf-8
# Project available at https://github.com/denexapp/advanced-status-vk
from typing import Iterable, Any


class BaseData:
    def __init__(self):
        self._users = dict()

    def _add_user(self, user: Any):
        self._users[user.user_id] = user  # type: Any

    def remove(self, user_id: str):
        self._users.pop(user_id)

    def is_user_exist(self, user_id: str) -> bool:
        return user_id in self._users

    def get_users(self) -> Iterable[Any]:
        return self._users.values()[:]

    def get_user(self, user_id: str) -> Any:
        return self._users[user_id]

