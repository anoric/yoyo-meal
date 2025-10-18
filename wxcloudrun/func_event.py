import logging
from sqlalchemy.exc import OperationalError
from wxcloudrun import db
from wxcloudrun.tables import Event, Notification

# 初始化日志
logger = logging.getLogger('log')


# ==================== 事件表相关操作 ====================
def query_event_by_id(event_id):
    """
    根据ID查询事件实体
    :param event_id: 事件ID
    :return: Event实体
    """
    try:
        return Event.query.filter(Event.id == event_id).first()
    except OperationalError as e:
        logger.info("query_event_by_id errorMsg= {} ".format(e))
        return None


def query_events_by_baby(baby_id):
    """
    根据宝宝ID查询事件列表
    :param baby_id: 宝宝ID
    :return: Event列表
    """
    try:
        return Event.query.filter(Event.baby_id == baby_id).order_by(Event.start_date.desc()).all()
    except OperationalError as e:
        logger.info("query_events_by_baby errorMsg= {} ".format(e))
        return []


def insert_event(event):
    """
    插入一个事件实体
    :param event: Event实体
    """
    try:
        db.session.add(event)
        db.session.commit()
        return True
    except OperationalError as e:
        logger.info("insert_event errorMsg= {} ".format(e))
        db.session.rollback()
        return False


def update_event(event_id, data):
    """
    更新事件信息
    :param event_id: 事件ID
    :param data: 更新数据字典
    """
    try:
        event = query_event_by_id(event_id)
        if event is None:
            return False
        
        if 'event_type' in data:
            event.event_type = data['event_type']
        if 'start_date' in data:
            event.start_date = data['start_date']
        if 'end_date' in data:
            event.end_date = data['end_date']
        if 'description' in data:
            event.description = data['description']
            
        db.session.commit()
        return True
    except OperationalError as e:
        logger.info("update_event errorMsg= {} ".format(e))
        db.session.rollback()
        return False


def delete_event(event_id):
    """
    删除事件
    :param event_id: 事件ID
    """
    try:
        event = Event.query.get(event_id)
        if event is None:
            return False
        db.session.delete(event)
        db.session.commit()
        return True
    except OperationalError as e:
        logger.info("delete_event errorMsg= {} ".format(e))
        db.session.rollback()
        return False


# ==================== 通知表相关操作 ====================
def query_notification_by_id(notification_id):
    """
    根据ID查询通知实体
    :param notification_id: 通知ID
    :return: Notification实体
    """
    try:
        return Notification.query.filter(Notification.id == notification_id).first()
    except OperationalError as e:
        logger.info("query_notification_by_id errorMsg= {} ".format(e))
        return None


def query_notifications_by_user(user_id, is_read=None):
    """
    根据用户ID查询通知列表
    :param user_id: 用户ID
    :param is_read: 是否已读（None表示查询全部）
    :return: Notification列表
    """
    try:
        query = Notification.query.filter(Notification.user_id == user_id)
        if is_read is not None:
            query = query.filter(Notification.is_read == is_read)
        return query.order_by(Notification.created_at.desc()).all()
    except OperationalError as e:
        logger.info("query_notifications_by_user errorMsg= {} ".format(e))
        return []


def insert_notification(notification):
    """
    插入一个通知实体
    :param notification: Notification实体
    """
    try:
        db.session.add(notification)
        db.session.commit()
        return True
    except OperationalError as e:
        logger.info("insert_notification errorMsg= {} ".format(e))
        db.session.rollback()
        return False


def mark_notification_read(notification_id):
    """
    标记通知为已读
    :param notification_id: 通知ID
    """
    try:
        notification = query_notification_by_id(notification_id)
        if notification is None:
            return False
        notification.is_read = True
        db.session.commit()
        return True
    except OperationalError as e:
        logger.info("mark_notification_read errorMsg= {} ".format(e))
        db.session.rollback()
        return False


def mark_all_notifications_read(user_id):
    """
    标记用户所有通知为已读
    :param user_id: 用户ID
    """
    try:
        Notification.query.filter(Notification.user_id == user_id).update({Notification.is_read: True})
        db.session.commit()
        return True
    except OperationalError as e:
        logger.info("mark_all_notifications_read errorMsg= {} ".format(e))
        db.session.rollback()
        return False


def delete_notification(notification_id):
    """
    删除通知
    :param notification_id: 通知ID
    """
    try:
        notification = Notification.query.get(notification_id)
        if notification is None:
            return False
        db.session.delete(notification)
        db.session.commit()
        return True
    except OperationalError as e:
        logger.info("delete_notification errorMsg= {} ".format(e))
        db.session.rollback()
        return False

