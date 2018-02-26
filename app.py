# coding=utf-8
# Project available at https://github.com/denexapp/advanced-status-vk
import time

import keys
from lastfm import LastFm
from vk import Vk


def main_loop():
    last_fm = LastFm(keys.last_fm_username, keys.last_fm_password, keys.last_fm_api_key, keys.last_fm_shared_secret)
    vk = Vk(keys.vk_access_token)
    default_status = vk.get_status()
    old_track_status = ""
    while True:
        track = last_fm.get_last_fm_now_playing(keys.last_fm_username)
        if track:
            new_track_status = 'Слушает {} - {} через Яндекс Музыку'.format(track.artist, track.name)
            if default_status is None:
                default_status = vk.get_status()
                vk.set_status(new_track_status)
            else:
                if old_track_status != new_track_status:
                    old_track_status = new_track_status
                    vk.set_status(new_track_status)
        else:
            if default_status:
                vk.set_status(default_status)
                default_status = None
        time.sleep(10)

if __name__ == '__main__':
    main_loop()
