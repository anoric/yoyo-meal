from datetime import datetime

from wxcloudrun import db


# 用户表
class User(db.Model):
    # 设置结构体表格名称
    __tablename__ = 'Users'

    # 设定结构体对应表格的字段
    uid = db.Column(db.String(50), primary_key=True)  # 用户唯一标识
    nickname = db.Column(db.String(100), nullable=False)  # 用户昵称
    avatar = db.Column(db.String(500))  # 用户头像URL
    created_at = db.Column('createdAt', db.TIMESTAMP, nullable=False, default=datetime.now())  # 创建时间
