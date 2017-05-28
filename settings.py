# -*- coding:utf-8 -*-
# Author: zhengdongjian@bytedance.com
# Create Time: Sun May 28 19:55:08 2017
import logging

DEBUG = False
LOG_LEVEL = logging.INFO


# filter white list for message forwarding
FILTER = [
    '8666',  # User RemarkName
    '冬',
]
if DEBUG:
    FILTER = []  # Will forward all messages when list is empty

REDIS_CONFIG = {
    'host': '127.0.0.1',
    'port': 6379,
    'db': 0,
}
EXPIRE_TIME = 3600  # Only hold messages in 1 hour


FWD_UID = 'filehelper'  # set to 'None' for yourself


STORAGE_DIR = './storage'


ITCHAT_LOGIN_CONFIG = {
    'hotReload': True,
    'enableCmdQR': True,
}
