# coding=utf-8
# Project available at https://github.com/denexapp/advanced-status-vk
import os

# Register your last.fm account here: https://www.last.fm/join
# last_fm_username = os.environ['last_fm_username']
# last_fm_password = os.environ['last_fm_password']

# Get an api and secret keys here: https://www.last.fm/api/account/create
last_fm_api_key = os.environ['last_fm_api_key']
last_fm_shared_secret = os.environ['last_fm_shared_secret']

# Register your vk page here: https://vk.com/join
# vk_user_id = ['vk_user_id']

# Register new standalone VK app here: https://vk.com/editapp?act=create
server_port = os.environ['PORT']

vk_app_client_id = os.environ['vk_app_client_id']
vk_app_client_secret = os.environ['vk_app_client_secret']

vk_group_id = os.environ['vk_group_id']
vk_group_access_token = os.environ['vk_group_access_token']

vk_auth_link = os.environ['vk_auth_link']

datastore_project_id = os.environ['datastore_project_id']
datastore_json = os.environ['datastore_json']

dialogflow_json = os.environ['dialogflow_json']