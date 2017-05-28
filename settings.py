# -*- coding:utf-8 -*-
# Author: zhengdongjian@bytedance.com
# Create Time: Sun May 28 19:55:08 2017
import logging

DEBUG = True

LOG_LEVEL = logging.INFO

FILTER = [
    '8666',  # Use RemarkName first, followed by NickName
]

if DEBUG:
    FILTER = []  # Empty FILTER to release all messages on debug mode

