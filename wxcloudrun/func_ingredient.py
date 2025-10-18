import logging
from sqlalchemy.exc import OperationalError
from wxcloudrun import db
from wxcloudrun.tables import Ingredient, FoodTrial

# 初始化日志
logger = logging.getLogger('log')


# ==================== 食材表相关操作 ====================
def query_ingredient_by_id(ingredient_id):
    """
    根据ID查询食材实体
    :param ingredient_id: 食材ID
    :return: Ingredient实体
    """
    try:
        return Ingredient.query.filter(Ingredient.id == ingredient_id).first()
    except OperationalError as e:
        logger.info("query_ingredient_by_id errorMsg= {} ".format(e))
        return None


def query_ingredients(page=1, page_size=20, category=None):
    """
    查询食材列表（分页）
    :param page: 页码
    :param page_size: 每页数量
    :param category: 分类筛选
    :return: 食材列表和总数
    """
    try:
        query = Ingredient.query
        if category:
            query = query.filter(Ingredient.category == category)
        
        total = query.count()
        ingredients = query.offset((page - 1) * page_size).limit(page_size).all()
        return ingredients, total
    except OperationalError as e:
        logger.info("query_ingredients errorMsg= {} ".format(e))
        return [], 0


def insert_ingredient(ingredient):
    """
    插入一个食材实体
    :param ingredient: Ingredient实体
    """
    try:
        db.session.add(ingredient)
        db.session.commit()
        return True
    except OperationalError as e:
        logger.info("insert_ingredient errorMsg= {} ".format(e))
        db.session.rollback()
        return False


def update_ingredient(ingredient_id, data):
    """
    更新食材信息
    :param ingredient_id: 食材ID
    :param data: 更新数据字典
    """
    try:
        ingredient = query_ingredient_by_id(ingredient_id)
        if ingredient is None:
            return False
        
        if 'name' in data:
            ingredient.name = data['name']
        if 'category' in data:
            ingredient.category = data['category']
        if 'image_url' in data:
            ingredient.image_url = data['image_url']
        if 'risk_level' in data:
            ingredient.risk_level = data['risk_level']
        if 'nutrients' in data:
            ingredient.nutrients = data['nutrients']
        if 'summary' in data:
            ingredient.summary = data['summary']
        if 'description' in data:
            ingredient.description = data['description']
        if 'suitable_month_from' in data:
            ingredient.suitable_month_from = data['suitable_month_from']
        if 'suitable_month_to' in data:
            ingredient.suitable_month_to = data['suitable_month_to']
            
        db.session.commit()
        return True
    except OperationalError as e:
        logger.info("update_ingredient errorMsg= {} ".format(e))
        db.session.rollback()
        return False


def delete_ingredient(ingredient_id):
    """
    删除食材
    :param ingredient_id: 食材ID
    """
    try:
        ingredient = Ingredient.query.get(ingredient_id)
        if ingredient is None:
            return False
        db.session.delete(ingredient)
        db.session.commit()
        return True
    except OperationalError as e:
        logger.info("delete_ingredient errorMsg= {} ".format(e))
        db.session.rollback()
        return False


# ==================== 食材尝试记录表相关操作 ====================
def query_food_trial_by_id(trial_id):
    """
    根据ID查询食材尝试记录
    :param trial_id: 记录ID
    :return: FoodTrial实体
    """
    try:
        return FoodTrial.query.filter(FoodTrial.id == trial_id).first()
    except OperationalError as e:
        logger.info("query_food_trial_by_id errorMsg= {} ".format(e))
        return None


def query_food_trials_by_baby(baby_id):
    """
    根据宝宝ID查询食材尝试记录列表
    :param baby_id: 宝宝ID
    :return: FoodTrial列表
    """
    try:
        return FoodTrial.query.filter(FoodTrial.baby_id == baby_id).all()
    except OperationalError as e:
        logger.info("query_food_trials_by_baby errorMsg= {} ".format(e))
        return []


def insert_food_trial(trial):
    """
    插入食材尝试记录
    :param trial: FoodTrial实体
    """
    try:
        db.session.add(trial)
        db.session.commit()
        return True
    except OperationalError as e:
        logger.info("insert_food_trial errorMsg= {} ".format(e))
        db.session.rollback()
        return False


def update_food_trial(trial_id, data):
    """
    更新食材尝试记录
    :param trial_id: 记录ID
    :param data: 更新数据字典
    """
    try:
        trial = query_food_trial_by_id(trial_id)
        if trial is None:
            return False
        
        if 'trial_date' in data:
            trial.trial_date = data['trial_date']
        if 'trial_count' in data:
            trial.trial_count = data['trial_count']
        if 'is_allergic' in data:
            trial.is_allergic = data['is_allergic']
        if 'reaction_level' in data:
            trial.reaction_level = data['reaction_level']
        if 'notes' in data:
            trial.notes = data['notes']
            
        db.session.commit()
        return True
    except OperationalError as e:
        logger.info("update_food_trial errorMsg= {} ".format(e))
        db.session.rollback()
        return False


def delete_food_trial(trial_id):
    """
    删除食材尝试记录
    :param trial_id: 记录ID
    """
    try:
        trial = FoodTrial.query.get(trial_id)
        if trial is None:
            return False
        db.session.delete(trial)
        db.session.commit()
        return True
    except OperationalError as e:
        logger.info("delete_food_trial errorMsg= {} ".format(e))
        db.session.rollback()
        return False

