class BotUser:
    def __init__(self, user_id: str, token: str = None):
        self.user_id = user_id  # type: str
        self.vk_token = token  # type: str
