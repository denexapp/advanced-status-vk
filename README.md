# Advanced status for vk
Allows to automatically broadcast your activity to status from other services. So far it supports broadcasting of now playing track using Last FM API(Yandex Music scrobbles to it). Program is ready to use in Heroku cloud(it has free python hosting).

## Requirements:
Python 3.6, `requests` and `requests_oauthlib` libraries.

## Setup
To make it work, you need to specify your access keys in keys.py file, detailed instructions can be found inside. You may replace them right in the file if you're planning to launch program locally. If you're planning to launch this on Heroku, use enviroment variables instead.
