from app.basedata import BaseData
from app.botuser import BotUser


class BotData(BaseData):
    def update_user(self, user_id: str, token: str = None):
        if token:
            self._users[user_id].token = token

    def add_user(self, user_id: str, token: str = None):
        user = BotUser(user_id, token=token)
        if token:
            self._users[user_id] = user
