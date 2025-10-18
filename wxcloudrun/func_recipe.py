import logging
from sqlalchemy.exc import OperationalError
from sqlalchemy import and_
from wxcloudrun import db
from wxcloudrun.tables import Recipe, RecipeItem

# 初始化日志
logger = logging.getLogger('log')


# ==================== 食谱主表相关操作 ====================
def query_recipe_by_id(recipe_id):
    """
    根据ID查询食谱实体
    :param recipe_id: 食谱ID
    :return: Recipe实体
    """
    try:
        return Recipe.query.filter(Recipe.id == recipe_id).first()
    except OperationalError as e:
        logger.info("query_recipe_by_id errorMsg= {} ".format(e))
        return None


def query_recipe_by_baby_and_date(baby_id, recipe_date):
    """
    根据宝宝ID和日期查询食谱
    :param baby_id: 宝宝ID
    :param recipe_date: 食谱日期
    :return: Recipe实体
    """
    try:
        return Recipe.query.filter(
            and_(Recipe.baby_id == baby_id, Recipe.recipe_date == recipe_date)
        ).first()
    except OperationalError as e:
        logger.info("query_recipe_by_baby_and_date errorMsg= {} ".format(e))
        return None


def query_recipes_by_baby(baby_id):
    """
    根据宝宝ID查询所有食谱
    :param baby_id: 宝宝ID
    :return: Recipe列表
    """
    try:
        return Recipe.query.filter(Recipe.baby_id == baby_id).order_by(Recipe.recipe_date.desc()).all()
    except OperationalError as e:
        logger.info("query_recipes_by_baby errorMsg= {} ".format(e))
        return []


def insert_recipe(recipe):
    """
    插入一个食谱实体
    :param recipe: Recipe实体
    """
    try:
        db.session.add(recipe)
        db.session.commit()
        return True
    except OperationalError as e:
        logger.info("insert_recipe errorMsg= {} ".format(e))
        db.session.rollback()
        return False


def update_recipe(recipe_id, data):
    """
    更新食谱信息
    :param recipe_id: 食谱ID
    :param data: 更新数据字典
    """
    try:
        recipe = query_recipe_by_id(recipe_id)
        if recipe is None:
            return False
        
        if 'notes' in data:
            recipe.notes = data['notes']
        if 'auto_generated' in data:
            recipe.auto_generated = data['auto_generated']
            
        db.session.commit()
        return True
    except OperationalError as e:
        logger.info("update_recipe errorMsg= {} ".format(e))
        db.session.rollback()
        return False


def delete_recipe(recipe_id):
    """
    删除食谱
    :param recipe_id: 食谱ID
    """
    try:
        recipe = Recipe.query.get(recipe_id)
        if recipe is None:
            return False
        db.session.delete(recipe)
        db.session.commit()
        return True
    except OperationalError as e:
        logger.info("delete_recipe errorMsg= {} ".format(e))
        db.session.rollback()
        return False


# ==================== 食谱项表相关操作 ====================
def query_recipe_item_by_id(item_id):
    """
    根据ID查询食谱项
    :param item_id: 食谱项ID
    :return: RecipeItem实体
    """
    try:
        return RecipeItem.query.filter(RecipeItem.id == item_id).first()
    except OperationalError as e:
        logger.info("query_recipe_item_by_id errorMsg= {} ".format(e))
        return None


def query_recipe_items(recipe_id):
    """
    根据食谱ID查询所有食谱项
    :param recipe_id: 食谱ID
    :return: RecipeItem列表
    """
    try:
        return RecipeItem.query.filter(RecipeItem.recipe_id == recipe_id).all()
    except OperationalError as e:
        logger.info("query_recipe_items errorMsg= {} ".format(e))
        return []


def insert_recipe_item(item):
    """
    插入食谱项
    :param item: RecipeItem实体
    """
    try:
        db.session.add(item)
        db.session.commit()
        return True
    except OperationalError as e:
        logger.info("insert_recipe_item errorMsg= {} ".format(e))
        db.session.rollback()
        return False


def update_recipe_item(item_id, data):
    """
    更新食谱项
    :param item_id: 食谱项ID
    :param data: 更新数据字典
    """
    try:
        item = query_recipe_item_by_id(item_id)
        if item is None:
            return False
        
        if 'meal_type' in data:
            item.meal_type = data['meal_type']
        if 'ingredients' in data:
            item.ingredients = data['ingredients']
        if 'instructions' in data:
            item.instructions = data['instructions']
            
        db.session.commit()
        return True
    except OperationalError as e:
        logger.info("update_recipe_item errorMsg= {} ".format(e))
        db.session.rollback()
        return False


def delete_recipe_item(item_id):
    """
    删除食谱项
    :param item_id: 食谱项ID
    """
    try:
        item = RecipeItem.query.get(item_id)
        if item is None:
            return False
        db.session.delete(item)
        db.session.commit()
        return True
    except OperationalError as e:
        logger.info("delete_recipe_item errorMsg= {} ".format(e))
        db.session.rollback()
        return False

