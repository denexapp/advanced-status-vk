from typing import List

from app.basedata import BaseData


class LastFmData(BaseData):
    class LastFmUser:
        def __init__(self, user_id: str, vk_user_id: str, track_name: str = None, track_artist: str = None):
            self.user_id: str = user_id
            self.vk_user_ids: List[str] = [vk_user_id]
            self.track_name: str = track_name
            self.track_artist: str = track_artist

    def update_user(self, user_id: str, vk_user_ids: List[str] = None, track_name: str = None, track_artist: str = None):
        if vk_user_ids:
            self._users[user_id].vk_user_ids = vk_user_ids
        if track_artist:
            self._users[user_id].track_artist = track_artist
        if track_name:
            self._users[user_id].track_name = track_name

    def add_user(self, user_id: str, vk_user_id: str, track_name: str = None, track_artist: str = None):
        user = LastFmData.LastFmUser(user_id, vk_user_id, track_name=track_name, track_artist=track_artist)
        self._users[user_id] = user

    def none_user(self, user_id: str, track_name: bool = False, track_artist: bool = False):
        if track_name:
            self._users[user_id].track_name = None
        if track_artist:
            self._users[user_id].track_artist = None
