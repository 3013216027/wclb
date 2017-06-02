# -*- coding: utf-8 -*-
# Author        : zhengdongjian@bytedance.com
# Create Time   : 2017/5/27 下午7:10
import datetime
import os
import re
import time
try:
    import ujson
except:
    import json as ujson

import itchat
from itchat.content import *

import settings
from settings import FILTER, DEBUG, FWD_UID, STORAGE_DIR
from util import logger
from db import DBS

TEXT_TYPE = [TEXT, MAP, CARD, SHARING]
FILE_TYPE = [PICTURE, RECORDING, ATTACHMENT, VIDEO]

REVOKE_MSG_ID = 10002
REVOKE_CONTENT_RE = re.compile(r'<msgid>(\d+)<')

db = DBS()


def get_time(ts=None):
    if not ts:
        dt = datetime.datetime.now()
    else:
        dt = datetime.datetime.fromtimestamp(ts)
    return dt.strftime('%y%m%dT%X')


def update_name(obj):
    """
    parse cname from json obj
    :param obj:
    :return:
    """
    if not obj:
        return
    username = obj.get('UserName')
    cname = obj.get('DisplayName') or obj.get('RemarkName') or obj.get('NickName')
    db.set_name(username, cname)
    logger.info('[update_name]set user name %s -> %s' % (username, cname))


def handle_name(user):
    """
    DisplayName is for group display only
    :param user: user data JSON
    :return:
    """
    update_name(user)
    update_name(user.get('Self'))
    member_list = user.get('MemberList')
    for member in member_list:
        update_name(member)


@itchat.msg_register(TEXT_TYPE, isFriendChat=True, isGroupChat=True)
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
    logger.info('[text_handle]%s' % ujson.dumps(msg, indent=2))
    from_user = msg.get('User')
    handle_name(from_user)
    cname = db.get_name(msg.get('ActualUserName') or msg.get('FromUserName'))
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
    db.set_msg(msg_id, message)
    if DEBUG:
        logger.debug('[text_handle]message stored: %s' % ujson.dumps(message, indent=2))
        fwd_msg = '[DEBUG]%s[%s@%s]' % (text, cname, create_time)
        itchat.send(fwd_msg, FWD_UID)


@itchat.msg_register(FILE_TYPE, isFriendChat=True, isGroupChat=True)
def file_handle(msg):
    """
    PICTURE: 图片、表情
    RECORDING: 录音
    ATTACHMENT: 附件
    VIDEO: 视频
    :param msg: 文件类信息
    :return:
    """
    logger.info('[file_handle]%s' % ujson.dumps(msg, indent=2))
    from_user = msg.get('User')
    handle_name(from_user)
    cname = db.get_name(msg.get('ActualUserName') or msg.get('FromUserName'))
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
    if (not FILTER) or cname in FILTER:
        msg['Text'](storage_name)  # only buffer files from those in filter list
        # post check
        file_size = os.path.getsize(storage_name)
        logger.debug('[file_handle]file_size of %s{msg_id=%s} is %s' % (storage_name, msg_id, file_size))
        if not file_size:
            logger.info('[file_handle]removed empty file %s{msg_id=%s}' % (storage_name, msg_id))
            os.remove(storage_name)
    db.set_msg(msg_id, message)
    if DEBUG:
        logger.debug('[file_handle]message stored: %s' % ujson.dumps(message, indent=2))
        fwd_msg = '[DEBUG]%s[%s@%s]' % (storage_name, cname, create_time)
        itchat.send(fwd_msg, FWD_UID)


@itchat.msg_register([NOTE], isFriendChat=True, isGroupChat=True)
def note_handle(msg):
    logger.info('[note_handle]%s' % ujson.dumps(msg, indent=2))
    msg_type_id = msg.get('MsgType')
    content = msg.get('Content')
    if msg_type_id != REVOKE_MSG_ID:
        return
    revoke_msg_id = REVOKE_CONTENT_RE.findall(content)
    if not revoke_msg_id:
        logger.error('[note_handle]MsgId not found!, body=%s' % ujson.dumps(msg, indent=2))
        return
    revoke_msg_id = revoke_msg_id[0]
    message = db.get_msg(revoke_msg_id)
    from_user = message.get('from_user')
    message_time = message.get('time')
    message_type = message.get('type')
    body = message.get('body')
    if message_type in TEXT_TYPE:
        text = body.get('text')
        fwd_msg = '%s[%s recall@%s]' % (text, from_user, message_time)
        itchat.send(fwd_msg, FWD_UID)
        logger.info('[note_handle]revoked text %s' % message)
    elif message_type in FILE_TYPE:
        file_name = body.get('file_name')
        storage_name = body.get('storage_name')
        if not os.path.exists(storage_name):
            logger.warning('[note_handle]File %s not exist!' % storage_name)
            return
        fwd_msg = '%s[%s recall@%s]' % (file_name, from_user, message_time)
        itchat.send(fwd_msg, FWD_UID)
        if message_type == PICTURE:
            itchat.send_image(storage_name, toUserName=FWD_UID)
        elif message_type == VIDEO:
            itchat.send_video(storage_name, toUserName=FWD_UID)
        else:
            itchat.send_file(storage_name, toUserName=FWD_UID)
        logger.info('[note_handle]revoked file %s' % message)
    else:
        logger.info('Unhandled message_type %s' % message_type)


@itchat.msg_register(FRIENDS)
def add_friend(msg):
    """
    FRIENDS: 添加好友请求
    :param msg:
    :return:
    """
    logger.info('[add_friend]request from %s' % (msg.get('Text')))
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
                os.remove(file_path)
                logger.info('[init.cleanup]removed %s' % file_path)
    # Set PID file
    pid = os.getpid()
    with open('wclb.pid', 'w') as f:
        f.write(str(pid))
    # Others
    if DEBUG:
        logger.debug('[init]DEBUG is on.')
    logger.info('[init]init finished.')


if __name__ == '__main__':
    init()
    itchat.auto_login(**settings.ITCHAT_LOGIN_CONFIG)
    try:
        itchat.run()
    except Exception as ex:
        logger.exception('[main]ex=%s' % ex)
