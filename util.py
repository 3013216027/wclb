# -*- coding:utf-8 -*-
# Author: zhengdongjian@bytedance.com
# Create Time: Sun May 28 19:31:32 2017
import logging
import logging.handlers
import settings

__all__ = ['logger']

logger = logging.getLogger(settings.LOG_CONFIG.get('logger_name'))
handler = logging.handlers.RotatingFileHandler(settings.LOG_CONFIG.get('filename'),
                                               maxBytes=settings.LOG_CONFIG.get('rotate_size'),
                                               backupCount=settings.LOG_CONFIG.get('rotate_count'))
formatter = logging.Formatter(settings.LOG_CONFIG.get('format'))
handler.setFormatter(formatter)
logger.addHandler(handler)

if settings.DEBUG:
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(settings.LOG_CONFIG.get('level'))


if __name__ == '__main__':
    logger.critical('critical')
    logger.error('error')
    logger.exception('exception')
    logger.warning('warning')
    logger.info('info')
    logger.debug('debug')
