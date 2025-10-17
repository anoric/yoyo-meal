import logging

from sqlalchemy.exc import OperationalError

from wxcloudrun import db
from wxcloudrun.model import Counters, User

# 初始化日志
logger = logging.getLogger('log')


def query_counterbyid(id):
    """
    根据ID查询Counter实体
    :param id: Counter的ID
    :return: Counter实体
    """
    try:
        return Counters.query.filter(Counters.id == id).first()
    except OperationalError as e:
        logger.info("query_counterbyid errorMsg= {} ".format(e))
        return None


def delete_counterbyid(id):
    """
    根据ID删除Counter实体
    :param id: Counter的ID
    """
    try:
        counter = Counters.query.get(id)
        if counter is None:
            return
        db.session.delete(counter)
        db.session.commit()
    except OperationalError as e:
        logger.info("delete_counterbyid errorMsg= {} ".format(e))


def insert_counter(counter):
    """
    插入一个Counter实体
    :param counter: Counters实体
    """
    try:
        db.session.add(counter)
        db.session.commit()
    except OperationalError as e:
        logger.info("insert_counter errorMsg= {} ".format(e))


def update_counterbyid(counter):
    """
    根据ID更新counter的值
    :param counter实体
    """
    try:
        counter = query_counterbyid(counter.id)
        if counter is None:
            return
        db.session.flush()
        db.session.commit()
    except OperationalError as e:
        logger.info("update_counterbyid errorMsg= {} ".format(e))


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
