# -*- coding:utf-8 -*-
# Author: zhengdongjian@bytedance.com
# Create Time: Sun May 28 19:55:08 2017
import logging

DEBUG = False

LOG_LEVEL = logging.INFO  # CRITICAL, ERROR, WARNING, INFO, DEBUG

FILTER = [
    '8666',
]

if DEBUG:
    FILTER = []  # empty FILTER to release all messages on debug mode

