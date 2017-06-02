# -*- coding: utf-8 -*-
# Author        : zhengdongjian@bytedance.com
# Create Time   : 2017/5/28 下午11:09
import sys
import redis
import ujson

from util import logger
from settings import REDIS_CONFIG, EXPIRE_TIME, USER_POLICY

__all__ = ['DBS']


class DBS(object):
    """
    collection for messages and user storage
    """
    USER_HASH = 'user'
    USER_EXPIRE = 3600 * 18

    def __init__(self):
        try:
            self.server = redis.Redis(**REDIS_CONFIG)
        except Exception as ex:
            logger.exception('Error when connecting to redis server, ex=%s' % ex)
            sys.exit(1)

    # r.publish('test', 'this will reach the listener')
    def get_msg(self, msg_id):
        """
        get message content by ID
        :param msg_id:
        :return:
        """
        message = self.server.get(msg_id) or b'{}'
        return ujson.loads(message.decode())

    def set_msg(self, msg_id, message_content):
        """
        store a message
        :param msg_id:
        :param message_content:
        :return:
        """
        self.server.set(msg_id, ujson.dumps(message_content), ex=EXPIRE_TIME)

    def get_name(self, username):
        """
        get cname for username(@something)
        :param username:
        :return:
        """
        if USER_POLICY == 'hashmap':
            return self.server.hget(DBS.USER_HASH, username).decode()
        else:
            return self.server.get(username).decode()

    def set_name(self, username, cname):
        """
        set cname for username(@something)
        :param username:
        :param cname:
        :return:
        """
        if USER_POLICY == 'hashmap':
            self.server.expire(DBS.USER_HASH, DBS.USER_EXPIRE)
            self.server.hset(DBS.USER_HASH, username, cname)
        else:
            self.server.set(username, cname, ex=DBS.USER_EXPIRE)

    def __getitem__(self, item):
        """
        same as get_msg
        :param item:
        :return:
        """
        return self.get_msg(item)

    def __setitem__(self, key, value):
        """
        same as set_msg
        :param key:
        :param value:
        :return:
        """
        self.set_msg(key, value)


if __name__ == '__main__':
    ms = DBS()
    ms.set_msg('test', {'a': 1, 'b': 2})
    res = ms.get_msg('test')
    print(ujson.dumps(res, indent=2))