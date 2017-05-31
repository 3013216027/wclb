# -*- coding: utf-8 -*-
# Author        : zhengdongjian@bytedance.com
# Create Time   : 2017/5/28 下午11:09
import sys
import redis
import ujson

from util import logger
from settings import REDIS_CONFIG, EXPIRE_TIME

__all__ = ['MessageSet']


class MessageSet(object):
    """
    MessageSet to store all messages that will have chance to be invoked.
    """
    def __init__(self):
        try:
            self.server = redis.Redis(**REDIS_CONFIG)
        except Exception as ex:
            logger.exception('Error when connecting to redis server, ex=%s' % ex)
            sys.exit(1)

    def get(self, msg_id):
        """
        get message content by ID
        :param msg_id:
        :return:
        """
        message = self.server.get(msg_id) or b'{}'
        return ujson.loads(message.decode())

    def set(self, msg_id, message_content):
        """
        store a message
        :param msg_id:
        :param message_content:
        :return:
        """
        self.server.set(msg_id, ujson.dumps(message_content), ex=EXPIRE_TIME)

    def __getitem__(self, item):
        return self.get(item)

    def __setitem__(self, key, value):
        self.set(key, value)


if __name__ == '__main__':
    ms = MessageSet()
    ms.set('test', {'a': 1, 'b': 2})
    res = ms.get('test')
    print(ujson.dumps(res, indent=2))
