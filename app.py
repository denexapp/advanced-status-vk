# coding=utf-8
# Project available at https://github.com/denexapp/advanced-status-vk
import time
from logging import info

import keys
from lastfm import LastFm
from vk import Vk


def main_loop():
    last_fm = LastFm(keys.last_fm_username, keys.last_fm_password, keys.last_fm_api_key, keys.last_fm_shared_secret)
    vk = Vk(keys.vk_access_token)
    default_status = vk.get_status()
    info('Received default status from vk: {}'.format(default_status))
    old_track_status = ""
    while True:
        info('Loop started')
        track = last_fm.get_last_fm_now_playing(keys.last_fm_username)
        if track:
            info('Now playing track:{}'.format(track.name))
            new_track_status = 'Слушает {} - {} через Яндекс Музыку'.format(track.artist, track.name)
            if default_status is None:
                default_status = vk.get_status()
                info('Default status is none, setting default: {}'.format(default_status))
                vk.set_status(new_track_status)
                info('Setting new status on vk: {}'.format(default_status))
            else:
                info('Default status: {}'.format(default_status))
                if old_track_status != new_track_status:
                    info('Old track status differs from new, setting to: {}'.format(new_track_status))
                    old_track_status = new_track_status
                    vk.set_status(new_track_status)
                else:
                    info('Old track status and new are the same: {}'.format(new_track_status))
        else:
            info('No now playing track')
            if default_status:
                info('Default status exist, setting it to vk: {}'.format(default_status))
                vk.set_status(default_status)
                default_status = None
            else:
                info('Default status is None')
        info('Loop ended')
        time.sleep(10)

if __name__ == '__main__':
    main_loop()
