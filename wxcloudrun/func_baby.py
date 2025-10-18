import logging
from sqlalchemy.exc import OperationalError
from wxcloudrun import db
from wxcloudrun.tables import Baby

# 初始化日志
logger = logging.getLogger('log')


# ==================== 宝宝表相关操作 ====================
def query_baby_by_id(baby_id):
    """
    根据ID查询宝宝实体
    :param baby_id: 宝宝ID
    :return: Baby实体
    """
    try:
        return Baby.query.filter(Baby.id == baby_id).first()
    except OperationalError as e:
        logger.info("query_baby_by_id errorMsg= {} ".format(e))
        return None


def query_babies_by_family(family_id):
    """
    根据家庭ID查询宝宝列表
    :param family_id: 家庭ID
    :return: Baby列表
    """
    try:
        return Baby.query.filter(Baby.family_id == family_id).all()
    except OperationalError as e:
        logger.info("query_babies_by_family errorMsg= {} ".format(e))
        return []


def insert_baby(baby):
    """
    插入一个宝宝实体
    :param baby: Baby实体
    """
    try:
        db.session.add(baby)
        db.session.commit()
        return True
    except OperationalError as e:
        logger.info("insert_baby errorMsg= {} ".format(e))
        db.session.rollback()
        return False


def update_baby(baby_id, data):
    """
    更新宝宝信息
    :param baby_id: 宝宝ID
    :param data: 更新数据字典
    """
    try:
        baby = query_baby_by_id(baby_id)
        if baby is None:
            return False
        
        if 'nickname' in data:
            baby.nickname = data['nickname']
        if 'gender' in data:
            baby.gender = data['gender']
        if 'birth_date' in data:
            baby.birth_date = data['birth_date']
        if 'avatar_url' in data:
            baby.avatar_url = data['avatar_url']
        if 'avoid_ingredients' in data:
            baby.avoid_ingredients = data['avoid_ingredients']
            
        db.session.commit()
        return True
    except OperationalError as e:
        logger.info("update_baby errorMsg= {} ".format(e))
        db.session.rollback()
        return False


def delete_baby(baby_id):
    """
    删除宝宝
    :param baby_id: 宝宝ID
    """
    try:
        baby = Baby.query.get(baby_id)
        if baby is None:
            return False
        db.session.delete(baby)
        db.session.commit()
        return True
    except OperationalError as e:
        logger.info("delete_baby errorMsg= {} ".format(e))
        db.session.rollback()
        return False

