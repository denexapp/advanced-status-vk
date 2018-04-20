from app.basedata import BaseData


class BotData(BaseData):
    class BotUser:
        def __init__(self, user_id: str, last_fm_id: str = None, token: str = None):
            self.user_id: str = user_id
            self.last_fm_id: str = last_fm_id
            self.vk_token: str = token

    def update_user(self, user_id: str, last_fm_id: str = None, token: str = None):
        if token:
            self._users[user_id].vk_token = token
        if last_fm_id:
            self._users[user_id].last_fm_id = last_fm_id

    def add_user(self, user_id: str, last_fm_id: str = None, token: str = None):
        user = BotData.BotUser(user_id, last_fm_id=last_fm_id, token=token)
        self._users[user_id] = user

    def none_user(self, user_id: str, last_fm_id: bool = False, token: bool = False):
        if token:
            self._users[user_id].vk_token = None
        if last_fm_id:
            self._users[user_id].last_fm_id = None
