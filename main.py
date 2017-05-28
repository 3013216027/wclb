# -*- coding: utf-8 -*-
# Author        : zhengdongjian@bytedance.com
# Create Time   : 2017/5/27 下午7:10
import os
import json
import itchat
import shutil
import datetime
from itchat.content import *

from util import logger

FWD_UID = None  # send messages to yourself
STORAGE_DIR = './storage'
NAME_MAP = {
}


def get_time():
    return datetime.datetime.now().strftime('%y%m%dT%X')


@itchat.msg_register([SYSTEM])
def system_handle(msg):
    """
    动态更新昵称和UserName映射表
    """
    logger.debug('system_handle called')
    user = msg.get('User')
    if user:
        # print(json.dumps(user, indent=2))
        username = user.get('UserName')
        cname = user.get('RemarkName') or user.get('NickName')
        if username and cname:
            NAME_MAP[username] = cname
            logger.debug('username table updated: %s -> %s' % (username, cname))
        else:
            logger.debug('error while parse system_handle %s' % (json.dumps(user)))


@itchat.msg_register([TEXT, MAP, CARD, NOTE, SHARING], isFriendChat=True, isGroupChat=True)
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
    from_user = msg['FromUserName']
    logger.debug('text_handle called')
    if (not NAME_MAP) or from_user in NAME_MAP:
        fwd_msg = '%s[%s@%s]' % (msg['Text'], NAME_MAP.get(from_user, from_user), get_time())
        logger.info(fwd_msg)
        itchat.send(fwd_msg, FWD_UID)
    else:
        logger.debug('%s: %s' % (from_user, msg['Text']))


@itchat.msg_register([PICTURE, RECORDING, ATTACHMENT, VIDEO], isFriendChat=True)
def file_handle(msg):
    """
    PICTURE: 图片、表情
    RECORDING: 录音
    ATTACHMENT: 附件
    VIDEO: 视频
    :param msg: 文件类信息
    :return:
    """
    file_name = msg['FileName']
    file_type = msg['Type']
    from_user = msg['FromUserName']
    logger.debug('file_handle called')
    if (not NAME_MAP) or msg['FromUserName'] in NAME_MAP:
        msg['Text'](file_name)
        fwd_msg = '%s[%s@%s]' % (file_name, NAME_MAP.get(from_user, from_user), get_time())
        logger.info(fwd_msg)
        itchat.send(fwd_msg, FWD_UID)
        file_dir = os.path.join(STORAGE_DIR, file_name)
        shutil.move(file_name, file_dir)
        if file_type == PICTURE:
            itchat.send_image(file_dir, toUserName=FWD_UID)
        elif file_type == VIDEO:
            itchat.send_video(file_dir, toUserName=FWD_UID)
        else:
            itchat.send_file(file_dir, toUserName=FWD_UID)
        # return '@%s@%s' % ({'Picture': 'img', 'Video': 'vid'}.get(msg['Type'], 'fil'), msg['FileName'])


@itchat.msg_register(FRIENDS)
def add_friend(msg):
    """
    FRIENDS: 添加好友请求
    :param msg:
    :return:
    """
    logger.debug('add_friend called')
    logger.info('get add_friend request from %s' % (msg['Text']))
    # itchat.add_friend(**msg['Text']) # 该操作会自动将新好友的消息录入，不需要重载通讯录
    # itchat.send_msg('Nice to meet you!', msg['RecommendInfo']['UserName'])


def init():
    # make directory for storage
    global NAME_MAP
    if not os.path.exists(STORAGE_DIR):
        try:
            os.mkdir(STORAGE_DIR)
        except Exception as e:
            logger.exception('[init.make_dir]ex=%s' % e)

    # add myself to filter list in debug mode
    NAME_MAP = {}
    logger.debug('DEBUG is on.')
    logger.info('init finished.')


if __name__ == '__main__':
    init()
    itchat.auto_login(hotReload=True, enableCmdQR=True)
    itchat.run()

