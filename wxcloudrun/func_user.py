import logging

from sqlalchemy.exc import OperationalError

from wxcloudrun import db
from wxcloudrun.tables import User

# 初始化日志
logger = logging.getLogger('log')


# ==================== 用户表相关操作 ====================
def query_user_by_uid(uid):
    """
    根据UID查询用户实体
    :param uid: 用户唯一标识
    :return: User实体
    """
    try:
        return User.query.filter(User.uid == uid).first()
    except OperationalError as e:
        logger.info("query_user_by_uid errorMsg= {} ".format(e))
        return None


def query_user_by_openid(openid):
    """
    根据微信openid查询用户实体
    :param openid: 微信用户唯一标识
    :return: User实体
    """
    try:
        return User.query.filter(User.uid == openid).first()
    except OperationalError as e:
        logger.info("query_user_by_openid errorMsg= {} ".format(e))
        return None


def insert_user(user):
    """
    插入一个用户实体
    :param user: User实体
    """
    try:
        db.session.add(user)
        db.session.commit()
    except OperationalError as e:
        logger.info("insert_user errorMsg= {} ".format(e))


def update_user_by_uid(user):
    """
    根据UID更新用户信息
    :param user: User实体
    """
    try:
        existing_user = query_user_by_uid(user.uid)
        if existing_user is None:
            return False
        existing_user.nickname = user.nickname
        existing_user.avatar = user.avatar
        db.session.commit()
        return True
    except OperationalError as e:
        logger.info("update_user_by_uid errorMsg= {} ".format(e))
        return False


def delete_user_by_uid(uid):
    """
    根据UID删除用户
    :param uid: 用户唯一标识
    """
    try:
        user = User.query.get(uid)
        if user is None:
            return False
        db.session.delete(user)
        db.session.commit()
        return True
    except OperationalError as e:
        logger.info("delete_user_by_uid errorMsg= {} ".format(e))
        return False
