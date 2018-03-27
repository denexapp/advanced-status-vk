# coding=utf-8
# Project available at https://github.com/denexapp/advanced-status-vk
import asyncio

import aiohttp

import app.keys as keys
from app.vk import Vk
from app.server import Server
from app.data import Data


def main_loop():
    loop = asyncio.get_event_loop()
    session = aiohttp.ClientSession(loop=loop)
    data = Data()
    vk = Vk(keys.vk_group_id, keys.vk_group_access_token, loop, session, data)
    server = Server(data, session, loop)
    loop.create_task(server.run())
    loop.create_task(vk.run_long_poll())
    loop.run_forever()

if __name__ == '__main__':
    main_loop()
