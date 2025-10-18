import logging

from sqlalchemy.exc import OperationalError

from wxcloudrun import db
from wxcloudrun.tables import User

# 初始化日志
logger = logging.getLogger('log')


# ==================== 用户表相关操作 ====================
def query_user_by_id(user_id):
    """
    根据ID查询用户实体
    :param user_id: 用户ID
    :return: User实体
    """
    try:
        return User.query.filter(User.id == user_id).first()
    except OperationalError as e:
        logger.info("query_user_by_id errorMsg= {} ".format(e))
        return None


def query_user_by_openid(openid):
    """
    根据微信openid查询用户实体
    :param openid: 微信用户唯一标识（存储在id字段）
    :return: User实体
    """
    try:
        return User.query.filter(User.id == openid).first()
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


def update_user_by_id(user_id, data):
    """
    根据ID更新用户信息
    :param user_id: 用户ID
    :param data: 更新数据字典
    """
    try:
        existing_user = query_user_by_id(user_id)
        if existing_user is None:
            return False
        if 'nickname' in data:
            existing_user.nickname = data['nickname']
        if 'avatar_url' in data:
            existing_user.avatar_url = data['avatar_url']
        db.session.commit()
        return True
    except OperationalError as e:
        logger.info("update_user_by_id errorMsg= {} ".format(e))
        db.session.rollback()
        return False


def delete_user_by_id(user_id):
    """
    根据ID删除用户
    :param user_id: 用户ID
    """
    try:
        user = User.query.get(user_id)
        if user is None:
            return False
        db.session.delete(user)
        db.session.commit()
        return True
    except OperationalError as e:
        logger.info("delete_user_by_id errorMsg= {} ".format(e))
        db.session.rollback()
        return False
