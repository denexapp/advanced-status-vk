# coding=utf-8
# Project available at https://github.com/denexapp/advanced-status-vk
import asyncio

import aiohttp

import app.keys as keys
from app.bot import Bot


def start_bot():
    loop = asyncio.get_event_loop()
    session = aiohttp.ClientSession(loop=loop)
    # server = Server(data, session, loop)
    # loop.create_task(server.run())
    bot = Bot(keys.vk_group_id, keys.vk_group_access_token, loop, session)
    loop.create_task(bot.run_bot())
    loop.run_forever()


if __name__ == '__main__':
    start_bot()
