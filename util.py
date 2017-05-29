# -*- coding:utf-8 -*-
# Author: zhengdongjian@bytedance.com
# Create Time: Sun May 28 19:31:32 2017
import logging
import settings

logger = logging.getLogger('wclb')
handler = logging.StreamHandler()
formatter = logging.Formatter(settings.LOG_FORMAT)
handler.setFormatter(formatter)
logger.addHandler(handler)

if settings.DEBUG:
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(settings.LOG_LEVEL)


if __name__ == '__main__':
    logger.critical('critical')
    logger.error('error')
    logger.exception('exception')
    logger.warning('warning')
    logger.info('info')
    logger.debug('debug')
