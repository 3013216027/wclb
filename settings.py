# -*- coding:utf-8 -*-
# Author: zhengdongjian@bytedance.com
# Create Time: Sun May 28 19:55:08 2017
import logging

DEBUG = False
LOG_LEVEL = logging.INFO
LOG_FORMAT = '%(levelname)s %(asctime)s %(filename)s:%(lineno)s data=%(message)s'

# Filter list for file storage
FILTER = [
    # '8666',  # User RemarkName
    # '冬',  # User NickName
]
if DEBUG:
    FILTER = []  # Will buffer all files on DEBUG mode

# Message buffered with redis.
REDIS_CONFIG = {
    'host': '127.0.0.1',
    'port': 6379,
    'db': 0,
}
EXPIRE_TIME = 3600 * 24  # Only hold messages within * seconds
USER_POLICY = ['default', 'hashmap'][1]  # policy for user cname storage

# Forward UserName
FWD_UID = 'filehelper'
# Forward back a message to the same chat
FWD_BACK = {
    'friend': False,
    'group': True,
}

# Storage settings
STORAGE_DIR = './storage'  # Directory for file storage
CLEANUP_ON_STARTUP = True  # Cleanup old files on init/startup phase
CLEANUP_THRESHOLD = 3600 * 24 * 3  # Only clean files older than * seconds

# Configuration for itchat auto login
ITCHAT_LOGIN_CONFIG = {
    'hotReload': True,
    'enableCmdQR': 2,  # Change to True may fix terminal width problem
}
