from app.basedata import BaseData


class BotData(BaseData):
    class BotUser:
        def __init__(self, user_id: str, token: str = None):
            self.user_id: str = user_id
            self.vk_token: str = token

    def update_user(self, user_id: str, token: str = None):
        if token:
            self._users[user_id].vk_token = token

    def add_user(self, user_id: str, token: str = None):
        user = BotData.BotUser(user_id, token=token)
        self._users[user_id] = user

    def none_user(self, user_id: str, token: bool = False):
        if token:
            self._users[user_id].vk_token = None
