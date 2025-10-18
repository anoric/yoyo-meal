from datetime import datetime

from wxcloudrun import db


# 用户表
class User(db.Model):
    # 设置结构体表格名称
    __tablename__ = 'users'

    # 设定结构体对应表格的字段
    id = db.Column(db.String(36), primary_key=True)  # 用户ID
    nickname = db.Column(db.String(100))  # 用户昵称
    avatar_url = db.Column(db.String(255))  # 用户头像URL
    created_at = db.Column(db.DateTime(3), nullable=False, default=datetime.now)  # 创建时间


# 家庭表
class Family(db.Model):
    __tablename__ = 'families'
    
    id = db.Column(db.String(36), primary_key=True)  # 家庭ID
    name = db.Column(db.String(100), nullable=False)  # 家庭名称
    created_by = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)  # 创建者用户ID
    created_at = db.Column(db.DateTime(3), nullable=False, default=datetime.now)  # 创建时间


# 家庭成员表
class FamilyMember(db.Model):
    __tablename__ = 'family_members'
    
    family_id = db.Column(db.String(36), db.ForeignKey('families.id'), primary_key=True)  # 家庭ID
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), primary_key=True)  # 用户ID
    role = db.Column(db.Enum('admin', 'member'), default='member')  # 成员角色
    joined_at = db.Column(db.DateTime(3), nullable=False, default=datetime.now)  # 加入时间


# 宝宝表
class Baby(db.Model):
    __tablename__ = 'babies'
    
    id = db.Column(db.String(36), primary_key=True)  # 宝宝ID
    family_id = db.Column(db.String(36), db.ForeignKey('families.id'), nullable=False)  # 所属家庭ID
    nickname = db.Column(db.String(100), nullable=False)  # 宝宝昵称
    gender = db.Column(db.Enum('M', 'F'), nullable=False)  # 性别
    birth_date = db.Column(db.Date, nullable=False)  # 出生日期
    avatar_url = db.Column(db.String(255))  # 头像URL
    avoid_ingredients = db.Column(db.JSON)  # 避免食材列表
    created_at = db.Column(db.DateTime(3), nullable=False, default=datetime.now)  # 创建时间


# 食材表
class Ingredient(db.Model):
    __tablename__ = 'ingredients'
    
    id = db.Column(db.String(36), primary_key=True)  # 食材ID
    name = db.Column(db.String(100), nullable=False)  # 食材名称
    category = db.Column(db.String(50))  # 分类
    image_url = db.Column(db.String(255))  # 插画或图片URL
    risk_level = db.Column(db.Enum('low', 'medium', 'high'), default='low')  # 过敏风险等级
    nutrients = db.Column(db.JSON)  # 营养构成
    summary = db.Column(db.String(255))  # 简述
    description = db.Column(db.Text)  # 详细描述
    suitable_month_from = db.Column(db.Integer)  # 适用起始月龄
    suitable_month_to = db.Column(db.Integer)  # 适用截止月龄
    updated_at = db.Column(db.DateTime(3), nullable=False, default=datetime.now, onupdate=datetime.now)  # 最后更新时间


# 食材尝试记录表
class FoodTrial(db.Model):
    __tablename__ = 'food_trials'
    
    id = db.Column(db.String(36), primary_key=True)  # 尝试记录ID
    baby_id = db.Column(db.String(36), db.ForeignKey('babies.id'), nullable=False)  # 宝宝ID
    ingredient_id = db.Column(db.String(36), db.ForeignKey('ingredients.id'), nullable=False)  # 食材ID
    trial_date = db.Column(db.Date, nullable=False)  # 尝试日期
    trial_count = db.Column(db.Integer, default=1)  # 尝试次数
    is_allergic = db.Column(db.Boolean, default=False)  # 是否过敏
    reaction_level = db.Column(db.Enum('none', 'mild', 'moderate', 'severe'), default='none')  # 反应等级
    notes = db.Column(db.Text)  # 备注
    created_at = db.Column(db.DateTime(3), nullable=False, default=datetime.now)  # 记录创建时间


# 食谱主表
class Recipe(db.Model):
    __tablename__ = 'recipes'
    
    id = db.Column(db.String(36), primary_key=True)  # 食谱ID
    baby_id = db.Column(db.String(36), db.ForeignKey('babies.id'), nullable=False)  # 宝宝ID
    recipe_date = db.Column(db.Date, nullable=False)  # 食谱日期
    created_by = db.Column(db.String(36), db.ForeignKey('users.id'))  # 创建者用户ID
    auto_generated = db.Column(db.Boolean, default=True)  # 是否为系统自动生成
    notes = db.Column(db.Text)  # 备注说明
    created_at = db.Column(db.DateTime(3), nullable=False, default=datetime.now)  # 创建时间


# 食谱项表
class RecipeItem(db.Model):
    __tablename__ = 'recipe_items'
    
    id = db.Column(db.String(36), primary_key=True)  # 食谱项ID
    recipe_id = db.Column(db.String(36), db.ForeignKey('recipes.id'), nullable=False)  # 所属食谱ID
    meal_type = db.Column(db.Enum('breakfast', 'morning_snack', 'lunch', 'afternoon_snack', 'dinner'), nullable=False)  # 餐别
    ingredients = db.Column(db.JSON)  # 所用食材列表
    instructions = db.Column(db.Text)  # 制作说明
    created_at = db.Column(db.DateTime(3), nullable=False, default=datetime.now)  # 创建时间


# 特殊事件表
class Event(db.Model):
    __tablename__ = 'events'
    
    id = db.Column(db.String(36), primary_key=True)  # 事件ID
    baby_id = db.Column(db.String(36), db.ForeignKey('babies.id'), nullable=False)  # 宝宝ID
    event_type = db.Column(db.Enum('illness', 'vaccine', 'other'), nullable=False)  # 事件类型
    start_date = db.Column(db.Date, nullable=False)  # 事件开始日期
    end_date = db.Column(db.Date)  # 事件结束日期
    description = db.Column(db.Text)  # 描述说明
    created_at = db.Column(db.DateTime(3), nullable=False, default=datetime.now)  # 记录创建时间


# 通知表
class Notification(db.Model):
    __tablename__ = 'notifications'
    
    id = db.Column(db.String(36), primary_key=True)  # 通知ID
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)  # 接收用户ID
    type = db.Column(db.Enum('trial_reminder', 'recipe_update', 'event_alert'), nullable=False)  # 通知类型
    title = db.Column(db.String(255))  # 标题
    message = db.Column(db.Text)  # 内容
    is_read = db.Column(db.Boolean, default=False)  # 是否已读
    created_at = db.Column(db.DateTime(3), nullable=False, default=datetime.now)  # 通知创建时间
