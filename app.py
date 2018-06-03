# coding=utf-8
# Project available at https://github.com/denexapp/advanced-status-vk
import asyncio

import aiohttp

import app.keys as keys
from app.bot import Bot


def start_bot():
    loop = asyncio.get_event_loop()
    session = aiohttp.ClientSession(loop=loop)
    bot = loop.run_until_complete(Bot(keys.vk_group_id,
                                      keys.vk_group_access_token,
                                      keys.last_fm_api_key,
                                      keys.last_fm_shared_secret,
                                      keys.datastore_project_id,
                                      keys.datastore_json,
                                      keys.dialogflow_json,
                                      loop,
                                      session))
    bot.run_bot()
    loop.run_forever()


if __name__ == '__main__':
    start_bot()
