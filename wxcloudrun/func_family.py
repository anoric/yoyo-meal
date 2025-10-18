import logging
from sqlalchemy.exc import OperationalError
from wxcloudrun import db
from wxcloudrun.tables import Family, FamilyMember

# 初始化日志
logger = logging.getLogger('log')


# ==================== 家庭表相关操作 ====================
def query_family_by_id(family_id):
    """
    根据ID查询家庭实体
    :param family_id: 家庭ID
    :return: Family实体
    """
    try:
        return Family.query.filter(Family.id == family_id).first()
    except OperationalError as e:
        logger.info("query_family_by_id errorMsg= {} ".format(e))
        return None


def insert_family(family):
    """
    插入一个家庭实体
    :param family: Family实体
    """
    try:
        db.session.add(family)
        db.session.commit()
        return True
    except OperationalError as e:
        logger.info("insert_family errorMsg= {} ".format(e))
        db.session.rollback()
        return False


def update_family(family_id, name):
    """
    更新家庭信息
    :param family_id: 家庭ID
    :param name: 家庭名称
    """
    try:
        family = query_family_by_id(family_id)
        if family is None:
            return False
        family.name = name
        db.session.commit()
        return True
    except OperationalError as e:
        logger.info("update_family errorMsg= {} ".format(e))
        db.session.rollback()
        return False


def delete_family(family_id):
    """
    删除家庭
    :param family_id: 家庭ID
    """
    try:
        family = Family.query.get(family_id)
        if family is None:
            return False
        db.session.delete(family)
        db.session.commit()
        return True
    except OperationalError as e:
        logger.info("delete_family errorMsg= {} ".format(e))
        db.session.rollback()
        return False


# ==================== 家庭成员表相关操作 ====================
def query_family_members(family_id):
    """
    查询家庭成员列表
    :param family_id: 家庭ID
    :return: 成员列表
    """
    try:
        return FamilyMember.query.filter(FamilyMember.family_id == family_id).all()
    except OperationalError as e:
        logger.info("query_family_members errorMsg= {} ".format(e))
        return []


def query_family_member(family_id, user_id):
    """
    查询家庭成员
    :param family_id: 家庭ID
    :param user_id: 用户ID
    :return: FamilyMember实体
    """
    try:
        return FamilyMember.query.filter(
            FamilyMember.family_id == family_id,
            FamilyMember.user_id == user_id
        ).first()
    except OperationalError as e:
        logger.info("query_family_member errorMsg= {} ".format(e))
        return None


def insert_family_member(member):
    """
    添加家庭成员
    :param member: FamilyMember实体
    """
    try:
        db.session.add(member)
        db.session.commit()
        return True
    except OperationalError as e:
        logger.info("insert_family_member errorMsg= {} ".format(e))
        db.session.rollback()
        return False


def delete_family_member(family_id, user_id):
    """
    删除家庭成员
    :param family_id: 家庭ID
    :param user_id: 用户ID
    """
    try:
        member = query_family_member(family_id, user_id)
        if member is None:
            return False
        db.session.delete(member)
        db.session.commit()
        return True
    except OperationalError as e:
        logger.info("delete_family_member errorMsg= {} ".format(e))
        db.session.rollback()
        return False


def query_user_families(user_id):
    """
    查询用户所属的所有家庭
    :param user_id: 用户ID
    :return: 家庭列表
    """
    try:
        members = FamilyMember.query.filter(FamilyMember.user_id == user_id).all()
        family_ids = [member.family_id for member in members]
        families = Family.query.filter(Family.id.in_(family_ids)).all()
        return families
    except OperationalError as e:
        logger.info("query_user_families errorMsg= {} ".format(e))
        return []

