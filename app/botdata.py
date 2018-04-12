from app.basedata import BaseData


class BotData(BaseData):
    class BotUser:
        def __init__(self, user_id: str, token: str = None):
            self.user_id = user_id  # type: str
            self.vk_token = token  # type: str

    def update_user(self, user_id: str, token: str = None):
        if token:
            self._users[user_id].vk_token = token

    def add_user(self, user_id: str, token: str = None):
        user = BotData.BotUser(user_id, token=token)
        self._users[user_id] = user
