# -*- coding: utf-8 -*-
# Author        : zhengdongjian@bytedance.com
# Create Time   : 2017/5/27 下午7:10
import datetime
import os
import re
import time
import ujson

import itchat
from itchat.content import *

import settings
from settings import FILTER, DEBUG, FWD_UID, STORAGE_DIR
from util import logger
from db import MessageSet

TEXT_TYPE = [TEXT, MAP, CARD, SHARING]
FILE_TYPE = [PICTURE, RECORDING, ATTACHMENT, VIDEO]

REVOKE_MSG_ID = 10002
REVOKE_CONTENT_RE = re.compile(r'<msgid>(\d+)<')

message_set = MessageSet()


def get_time(ts=None):
    if not ts:
        dt = datetime.datetime.now()
    else:
        dt = datetime.datetime.fromtimestamp(ts)
    return dt.strftime('%y%m%dT%X')


def parse_name(user):
    return user.get('RemarkName', '') or user.get('NickName', '') or user.get('UserName')


@itchat.msg_register(TEXT_TYPE, isFriendChat=True)
def text_handle(msg):
    """
    TEXT: 文本
    MAP: 定位
    CARD: 名片
    NOTE: 通知
    SHARING: 分享链接
    :param msg: 文本类/可文本化消息
    :return:
    """
    logger.debug('text_handle called')
    logger.debug('%s' % ujson.dumps(msg, indent=2))
    from_user = msg.get('User')
    cname = parse_name(from_user)
    text = msg.get('Text')
    content = msg.get('Content')
    msg_type = msg.get('Type')
    msg_id = msg.get('MsgId')
    create_time = get_time(msg.get('CreateTime'))
    message = {
        # 'mid': msg_id,
        'from_user': cname,
        'type': msg_type,
        'time': create_time,
        'body': {
            'text': text,
            'content': content,
        },
    }
    message_set.set(msg_id, message)
    if DEBUG:
        logger.debug('message stored: %s' % ujson.dumps(message, indent=2))
        fwd_msg = '[DEBUG]%s[%s@%s]' % (text, cname, create_time)
        itchat.send(fwd_msg, FWD_UID)


@itchat.msg_register(FILE_TYPE, isFriendChat=True)
def file_handle(msg):
    """
    PICTURE: 图片、表情
    RECORDING: 录音
    ATTACHMENT: 附件
    VIDEO: 视频
    :param msg: 文件类信息
    :return:
    """
    logger.debug('file_handle called')
    logger.debug('%s' % ujson.dumps(msg, indent=2))
    from_user = msg.get('User')
    cname = parse_name(from_user)
    file_name = msg.get('FileName')
    storage_name = os.path.join(STORAGE_DIR, file_name)
    file_type = msg.get('Type')
    msg_id = msg.get('MsgId')
    content = msg.get('Content')
    create_time = get_time(msg.get('CreateTime'))
    message = {
        'from_user': cname,
        'type': file_type,
        'time': create_time,
        'body': {
            'file_name': file_name,
            'storage_name': storage_name,
            'content': content,
        },
    }
    message_set.set(msg_id, message)
    if (not FILTER) or cname in FILTER:
        msg['Text'](storage_name)  # only buffer files from those in filter list
    if DEBUG:
        logger.debug('message stored: %s' % ujson.dumps(message, indent=2))


@itchat.msg_register([NOTE])
def note_handle(msg):
    logger.debug('note_handle called')
    logger.debug('%s' % ujson.dumps(msg, indent=2))
    msg_type_id = msg.get('MsgType')
    content = msg.get('Content')
    if msg_type_id != REVOKE_MSG_ID:
        return
    revoke_msg_id = REVOKE_CONTENT_RE.findall(content)
    if not revoke_msg_id:
        logger.warning('MsgId not found!, body=%s' % ujson.dumps(msg, indent=2))
        return
    revoke_msg_id = revoke_msg_id[0]
    message = message_set.get(revoke_msg_id)
    from_user = message.get('from_user')
    message_time = message.get('time')
    message_type = message.get('type')
    body = message.get('body')
    if message_type in TEXT_TYPE:
        text = body.get('text')
        fwd_msg = '%s[%s@%s]' % (text, from_user, message_time)
        itchat.send(fwd_msg, FWD_UID)
    elif message_type in FILE_TYPE:
        file_name = body.get('file_name')
        storage_name = body.get('storage_name')
        if not os.path.exists(storage_name):
            logger.error('[note_handle]File %s not exist!' % storage_name)
            return
        fwd_msg = '%s[%s@%s]' % (file_name, from_user, message_time)
        itchat.send(fwd_msg, FWD_UID)
        if message_type == PICTURE:
            itchat.send_image(storage_name, toUserName=FWD_UID)
        elif message_type == VIDEO:
            itchat.send_video(storage_name, toUserName=FWD_UID)
        else:
            itchat.send_file(storage_name, toUserName=FWD_UID)
    else:
        logger.info('Unhandled message_type %s' % message_type)


@itchat.msg_register(FRIENDS)
def add_friend(msg):
    """
    FRIENDS: 添加好友请求
    :param msg:
    :return:
    """
    logger.debug('add_friend called')
    logger.info('get add_friend request from %s' % (msg.get('Text')))
    # itchat.add_friend(**msg['Text']) # 该操作会自动将新好友的消息录入，不需要重载通讯录
    # itchat.send_msg('Nice to meet you!', msg['RecommendInfo']['UserName'])


def init():
    # make directory for storage
    if not os.path.exists(STORAGE_DIR):
        try:
            os.mkdir(STORAGE_DIR)
        except Exception as ex:
            logger.exception('[init.make_dir]ex=%s' % ex)
    # cleanup old files
    if settings.CLEANUP_ON_STARTUP:
        current_time = time.time()
        for f in os.listdir(STORAGE_DIR):
            file_path = os.path.join(STORAGE_DIR, f)
            creation_time = os.path.getctime(file_path)
            if current_time - creation_time > settings.CLEANUP_THRESHOLD:
                os.unlink(file_path)
                logger.info('[init.cleanup]removed %s' % file_path)
    # Set PID file
    pid = os.getpid()
    with open('wclb.pid', 'w') as f:
        f.write(str(pid))
    # Others
    if DEBUG:
        logger.debug('DEBUG is on.')
    logger.info('init finished.')


if __name__ == '__main__':
    init()
    itchat.auto_login(**settings.ITCHAT_LOGIN_CONFIG)
    try:
        itchat.run()
    except Exception as ex:
        logger.exception('[init]ex=%s' % ex)
