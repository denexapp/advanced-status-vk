# coding=utf-8
# Project available at https://github.com/denexapp/advanced-status-vk
import time

import keys
from lastfm import LastFm
from vk import Vk


def main_loop():
    # last_fm = LastFm(keys.last_fm_username, keys.last_fm_password, keys.last_fm_api_key, keys.last_fm_shared_secret)
    # vk = Vk(keys.vk_access_token)
    # default_status = None
    # old_status = ""
    # while True:
    #     track = last_fm.get_last_fm_now_playing(keys.last_fm_username)
    #     if track:
    #         # print('Now playing track:{}'.format(track.name))
    #         new_status = 'Слушает {} - {} через Яндекс Музыку'.format(track.artist, track.name)
    #         if default_status is None:
    #             default_status = vk.get_status()
    #             # print('Default status is none, setting default: {}'.format(default_status))
    #             vk.set_status(new_status)
    #             # print('Setting new status on vk: {}'.format(new_status))
    #             old_status = new_status
    #             # print('Setting old status: {}'.format(old_status))
    #         else:
    #             # print('Default status: {}'.format(default_status))
    #             if old_status != new_status:
    #                 # print('Old track status differs from new, setting to: {}'.format(new_status))
    #                 old_status = new_status
    #                 vk.set_status(new_status)
    #             else:
    #                 # print('Old track status and new are the same: {}'.format(new_status))
    #     else:
    #         print('No now playing track')
    #         if default_status:
    #             # print('Default status exist, setting it to vk: {}'.format(default_status))
    #             vk.set_status(default_status)
    #             default_status = None
    #         else:
    #             # print('Default status is None')
    #     time.sleep(10)
    vk = Vk(keys.vk_group_id, keys.vk_group_access_token)
    vk.start_bot()

if __name__ == '__main__':
    main_loop()
