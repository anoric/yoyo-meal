from datetime import datetime, date
from flask import request
from run import app
import uuid
import requests
import config

# 导入所有表模型
from wxcloudrun.tables import User, Family, FamilyMember, Baby, Ingredient, FoodTrial, Recipe, RecipeItem, Event, Notification

# 导入用户相关函数
from wxcloudrun.func_user import query_user_by_id, query_user_by_openid, insert_user, update_user_by_id, delete_user_by_id

# 导入家庭相关函数
from wxcloudrun.func_family import (query_family_by_id, insert_family, update_family, delete_family,
                                     query_family_members, query_family_member, insert_family_member, 
                                     delete_family_member, query_user_families)

# 导入宝宝相关函数
from wxcloudrun.func_baby import query_baby_by_id, query_babies_by_family, insert_baby, update_baby, delete_baby

# 导入食材相关函数
from wxcloudrun.func_ingredient import (query_ingredient_by_id, query_ingredients, insert_ingredient, 
                                         update_ingredient, delete_ingredient,
                                         query_food_trial_by_id, query_food_trials_by_baby, 
                                         insert_food_trial, update_food_trial, delete_food_trial)

# 导入食谱相关函数
from wxcloudrun.func_recipe import (query_recipe_by_id, query_recipe_by_baby_and_date, query_recipes_by_baby,
                                     insert_recipe, update_recipe, delete_recipe,
                                     query_recipe_item_by_id, query_recipe_items, insert_recipe_item,
                                     update_recipe_item, delete_recipe_item)

# 导入事件相关函数
from wxcloudrun.func_event import (query_event_by_id, query_events_by_baby, insert_event, update_event, delete_event,
                                    query_notification_by_id, query_notifications_by_user, insert_notification,
                                    mark_notification_read, mark_all_notifications_read, delete_notification)

# 导入响应函数
from wxcloudrun.response import make_succ_response, make_succ_empty_response, make_err_response


# ==================== 微信小程序登录接口 ====================
@app.route('/api/auth/login', methods=['POST'])
def wechat_login():
    """
    微信小程序登录接口
    :return: 登录结果
    """
    params = request.get_json()

    # 检查必需参数
    if 'code' not in params:
        return make_err_response('缺少code参数')

    code = params['code']

    try:
        # 调用微信接口获取openid和session_key
        wechat_url = 'https://api.weixin.qq.com/sns/jscode2session'
        wechat_params = {
            'appid': config.WECHAT_APPID,
            'secret': config.WECHAT_SECRET,
            'js_code': code,
            'grant_type': 'authorization_code'
        }

        response = requests.get(wechat_url, params=wechat_params, timeout=10, verify=False)
        wechat_data = response.json()

        # 检查微信接口返回结果
        if 'errcode' in wechat_data and wechat_data['errcode'] != 0:
            error_msg = wechat_data.get('errmsg', '微信登录失败')
            return make_err_response(f'微信登录失败: {error_msg}')

        if 'openid' not in wechat_data:
            return make_err_response('微信登录失败: 未获取到openid')

        openid = wechat_data['openid']
        session_key = wechat_data.get('session_key', '')
        unionid = wechat_data.get('unionid', '')

        # 查询用户是否已存在
        existing_user = query_user_by_openid(openid)

        if existing_user:
            # 用户已存在，返回用户信息
            user_data = {
                'id': existing_user.id,
                'nickname': existing_user.nickname,
                'avatar_url': existing_user.avatar_url,
                'created_at': existing_user.created_at.isoformat(),
                'isNewUser': False
            }
        else:
            # 用户不存在，创建新用户
            user = User()
            user.id = openid  # 使用openid作为用户ID
            user.nickname = f'微信用户_{openid[-6:]}'  # 默认昵称
            user.avatar_url = ''  # 默认头像为空
            user.created_at = datetime.now()

            insert_user(user)

            user_data = {
                'id': user.id,
                'nickname': user.nickname,
                'avatar_url': user.avatar_url,
                'created_at': user.created_at.isoformat(),
                'isNewUser': True
            }

        # 返回登录成功结果
        return make_succ_response({
            'user': user_data,
            'sessionKey': session_key,
            'unionid': unionid
        })

    except requests.exceptions.Timeout:
        return make_err_response('微信登录超时，请稍后重试')
    except requests.exceptions.RequestException as e:
        return make_err_response(f'微信登录请求失败: {str(e)}')
    except Exception as e:
        return make_err_response(f'登录失败: {str(e)}')


# ==================== 用户相关接口 ====================
@app.route('/api/users/<user_id>', methods=['GET'])
def get_user(user_id):
    """
    根据ID获取用户信息
    :param user_id: 用户ID
    :return: 用户信息
    """
    user = query_user_by_id(user_id)
    if user is None:
        return make_err_response('用户不存在')

    return make_succ_response({
        'id': user.id,
        'nickname': user.nickname,
        'avatar_url': user.avatar_url,
        'created_at': user.created_at.isoformat()
    })


@app.route('/api/users/<user_id>', methods=['PATCH'])
def update_user(user_id):
    """
    更新用户信息
    :param user_id: 用户ID
    :return: 更新结果
    """
    params = request.get_json()

    # 检查用户是否存在
    existing_user = query_user_by_id(user_id)
    if existing_user is None:
        return make_err_response('用户不存在')

    # 更新用户信息
    success = update_user_by_id(user_id, params)
    if not success:
        return make_err_response('更新用户失败')

    # 返回更新后的用户信息
    updated_user = query_user_by_id(user_id)
    return make_succ_response({
        'id': updated_user.id,
        'nickname': updated_user.nickname,
        'avatar_url': updated_user.avatar_url,
        'created_at': updated_user.created_at.isoformat()
    })


@app.route('/api/users/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    """
    删除用户
    :param user_id: 用户ID
    :return: 删除结果
    """
    success = delete_user_by_id(user_id)
    if not success:
        return make_err_response('用户不存在或删除失败')

    return make_succ_empty_response()


# ==================== 家庭管理接口 ====================
@app.route('/api/families', methods=['POST'])
def create_family():
    """
    创建家庭
    :return: 家庭信息
    """
    params = request.get_json()
    
    if 'name' not in params or 'created_by' not in params:
        return make_err_response('缺少必需参数')
    
    # 创建家庭
    family = Family()
    family.id = str(uuid.uuid4())
    family.name = params['name']
    family.created_by = params['created_by']
    family.created_at = datetime.now()
    
    insert_family(family)
    
    # 将创建者添加为家庭管理员
    member = FamilyMember()
    member.family_id = family.id
    member.user_id = params['created_by']
    member.role = 'admin'
    member.joined_at = datetime.now()
    insert_family_member(member)
    
    return make_succ_response({
        'id': family.id,
        'name': family.name,
        'created_by': family.created_by,
        'created_at': family.created_at.isoformat()
    })


@app.route('/api/families/<family_id>', methods=['GET'])
def get_family(family_id):
    """
    获取家庭信息
    :param family_id: 家庭ID
    :return: 家庭信息
    """
    family = query_family_by_id(family_id)
    if family is None:
        return make_err_response('家庭不存在')
    
    return make_succ_response({
        'id': family.id,
        'name': family.name,
        'created_by': family.created_by,
        'created_at': family.created_at.isoformat()
    })


@app.route('/api/families/<family_id>/members', methods=['POST'])
def add_family_member(family_id):
    """
    添加家庭成员
    :param family_id: 家庭ID
    :return: 添加结果
    """
    params = request.get_json()
    
    if 'user_id' not in params:
        return make_err_response('缺少user_id参数')
    
    # 检查家庭是否存在
    family = query_family_by_id(family_id)
    if family is None:
        return make_err_response('家庭不存在')
    
    # 检查用户是否已是家庭成员
    existing_member = query_family_member(family_id, params['user_id'])
    if existing_member:
        return make_err_response('用户已是家庭成员')
    
    # 添加成员
    member = FamilyMember()
    member.family_id = family_id
    member.user_id = params['user_id']
    member.role = params.get('role', 'member')
    member.joined_at = datetime.now()
    
    insert_family_member(member)
    
    return make_succ_response({
        'family_id': member.family_id,
        'user_id': member.user_id,
        'role': member.role,
        'joined_at': member.joined_at.isoformat()
    })


@app.route('/api/families/<family_id>/members', methods=['GET'])
def get_family_members(family_id):
    """
    获取家庭成员列表
    :param family_id: 家庭ID
    :return: 成员列表
    """
    members = query_family_members(family_id)
    
    members_data = []
    for member in members:
        user = query_user_by_id(member.user_id)
        if user:
            members_data.append({
                'user_id': member.user_id,
                'nickname': user.nickname,
                'avatar_url': user.avatar_url,
                'role': member.role,
                'joined_at': member.joined_at.isoformat()
            })
    
    return make_succ_response(members_data)


@app.route('/api/users/<user_id>/families', methods=['GET'])
def get_user_families(user_id):
    """
    获取用户所属的家庭列表
    :param user_id: 用户ID
    :return: 家庭列表
    """
    families = query_user_families(user_id)
    
    families_data = [{
        'id': family.id,
        'name': family.name,
        'created_by': family.created_by,
        'created_at': family.created_at.isoformat()
    } for family in families]
    
    return make_succ_response(families_data)


# ==================== 宝宝管理接口 ====================
@app.route('/api/babies', methods=['POST'])
def create_baby():
    """
    添加宝宝
    如果用户没有家庭，自动创建一个家庭
    :return: 宝宝信息
    """
    params = request.get_json()
    
    # 检查必需参数（不再要求family_id，但需要created_by）
    required_fields = ['nickname', 'gender', 'birth_date', 'created_by']
    for field in required_fields:
        if field not in params:
            return make_err_response(f'缺少必需参数: {field}')
    
    # 检查用户是否存在
    user = query_user_by_id(params['created_by'])
    if user is None:
        return make_err_response('用户不存在')
    
    # 确定家庭ID
    family_id = params.get('family_id')
    
    # 如果没有提供family_id，检查用户是否有家庭
    if not family_id:
        user_families = query_user_families(params['created_by'])
        if user_families:
            # 用户已有家庭，使用第一个家庭
            family_id = user_families[0].id
        else:
            # 用户没有家庭，自动创建一个
            family = Family()
            family.id = str(uuid.uuid4())
            family.name = f"{params['nickname']}的家庭"
            family.created_by = params['created_by']
            family.created_at = datetime.now()
            
            insert_family(family)
            
            # 将创建者添加为家庭管理员
            member = FamilyMember()
            member.family_id = family.id
            member.user_id = params['created_by']
            member.role = 'admin'
            member.joined_at = datetime.now()
            insert_family_member(member)
            
            family_id = family.id
    else:
        # 验证家庭是否存在
        existing_family = query_family_by_id(family_id)
        if existing_family is None:
            return make_err_response('家庭不存在')
    
    # 创建宝宝
    baby = Baby()
    baby.id = str(uuid.uuid4())
    baby.family_id = family_id
    baby.nickname = params['nickname']
    baby.gender = params['gender']
    baby.birth_date = datetime.strptime(params['birth_date'], '%Y-%m-%d').date()
    baby.avatar_url = params.get('avatar_url', '')
    baby.avoid_ingredients = params.get('avoid_ingredients', [])
    baby.created_at = datetime.now()
    
    insert_baby(baby)
    
    return make_succ_response({
        'id': baby.id,
        'family_id': baby.family_id,
        'nickname': baby.nickname,
        'gender': baby.gender,
        'birth_date': baby.birth_date.isoformat(),
        'avatar_url': baby.avatar_url,
        'avoid_ingredients': baby.avoid_ingredients,
        'created_at': baby.created_at.isoformat()
    })


@app.route('/api/babies/<baby_id>', methods=['GET'])
def get_baby(baby_id):
    """
    获取宝宝信息
    :param baby_id: 宝宝ID
    :return: 宝宝信息
    """
    baby = query_baby_by_id(baby_id)
    if baby is None:
        return make_err_response('宝宝不存在')
    
    return make_succ_response({
        'id': baby.id,
        'family_id': baby.family_id,
        'nickname': baby.nickname,
        'gender': baby.gender,
        'birth_date': baby.birth_date.isoformat(),
        'avatar_url': baby.avatar_url,
        'avoid_ingredients': baby.avoid_ingredients,
        'created_at': baby.created_at.isoformat()
    })


@app.route('/api/families/<family_id>/babies', methods=['GET'])
def get_family_babies(family_id):
    """
    获取家庭下所有宝宝
    :param family_id: 家庭ID
    :return: 宝宝列表
    """
    babies = query_babies_by_family(family_id)
    
    babies_data = [{
        'id': baby.id,
        'family_id': baby.family_id,
        'nickname': baby.nickname,
        'gender': baby.gender,
        'birth_date': baby.birth_date.isoformat(),
        'avatar_url': baby.avatar_url,
        'avoid_ingredients': baby.avoid_ingredients,
        'created_at': baby.created_at.isoformat()
    } for baby in babies]
    
    return make_succ_response(babies_data)


@app.route('/api/babies/<baby_id>', methods=['PATCH'])
def update_baby_info(baby_id):
    """
    更新宝宝信息
    :param baby_id: 宝宝ID
    :return: 更新结果
    """
    params = request.get_json()
    
    # 检查宝宝是否存在
    existing_baby = query_baby_by_id(baby_id)
    if existing_baby is None:
        return make_err_response('宝宝不存在')
    
    # 处理日期格式
    if 'birth_date' in params:
        params['birth_date'] = datetime.strptime(params['birth_date'], '%Y-%m-%d').date()
    
    # 更新宝宝信息
    success = update_baby(baby_id, params)
    if not success:
        return make_err_response('更新宝宝信息失败')
    
    # 返回更新后的宝宝信息
    updated_baby = query_baby_by_id(baby_id)
    return make_succ_response({
        'id': updated_baby.id,
        'family_id': updated_baby.family_id,
        'nickname': updated_baby.nickname,
        'gender': updated_baby.gender,
        'birth_date': updated_baby.birth_date.isoformat(),
        'avatar_url': updated_baby.avatar_url,
        'avoid_ingredients': updated_baby.avoid_ingredients,
        'created_at': updated_baby.created_at.isoformat()
    })


@app.route('/api/babies/<baby_id>', methods=['DELETE'])
def delete_baby_info(baby_id):
    """
    删除宝宝
    :param baby_id: 宝宝ID
    :return: 删除结果
    """
    success = delete_baby(baby_id)
    if not success:
        return make_err_response('宝宝不存在或删除失败')
    
    return make_succ_empty_response()


# ==================== 食材库接口 ====================
@app.route('/api/ingredients', methods=['GET'])
def get_ingredients():
    """
    获取食材列表（分页）
    :return: 食材列表
    """
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 20, type=int)
    category = request.args.get('category', None)
    
    ingredients, total = query_ingredients(page, page_size, category)
    
    ingredients_data = [{
        'id': ingredient.id,
        'name': ingredient.name,
        'category': ingredient.category,
        'image_url': ingredient.image_url,
        'risk_level': ingredient.risk_level,
        'nutrients': ingredient.nutrients,
        'summary': ingredient.summary,
        'suitable_month_from': ingredient.suitable_month_from,
        'suitable_month_to': ingredient.suitable_month_to
    } for ingredient in ingredients]
    
    return make_succ_response({
        'ingredients': ingredients_data,
        'total': total,
        'page': page,
        'page_size': page_size
    })


@app.route('/api/ingredients/<ingredient_id>', methods=['GET'])
def get_ingredient(ingredient_id):
    """
    查看单个食材
    :param ingredient_id: 食材ID
    :return: 食材信息
    """
    ingredient = query_ingredient_by_id(ingredient_id)
    if ingredient is None:
        return make_err_response('食材不存在')
    
    return make_succ_response({
        'id': ingredient.id,
        'name': ingredient.name,
        'category': ingredient.category,
        'image_url': ingredient.image_url,
        'risk_level': ingredient.risk_level,
        'nutrients': ingredient.nutrients,
        'summary': ingredient.summary,
        'description': ingredient.description,
        'suitable_month_from': ingredient.suitable_month_from,
        'suitable_month_to': ingredient.suitable_month_to,
        'updated_at': ingredient.updated_at.isoformat()
    })


@app.route('/api/ingredients', methods=['POST'])
def create_ingredient():
    """
    添加新食材
    :return: 食材信息
    """
    params = request.get_json()
    
    if 'name' not in params:
        return make_err_response('缺少name参数')
    
    # 创建食材
    ingredient = Ingredient()
    ingredient.id = str(uuid.uuid4())
    ingredient.name = params['name']
    ingredient.category = params.get('category', '')
    ingredient.image_url = params.get('image_url', '')
    ingredient.risk_level = params.get('risk_level', 'low')
    ingredient.nutrients = params.get('nutrients', {})
    ingredient.summary = params.get('summary', '')
    ingredient.description = params.get('description', '')
    ingredient.suitable_month_from = params.get('suitable_month_from', None)
    ingredient.suitable_month_to = params.get('suitable_month_to', None)
    ingredient.updated_at = datetime.now()
    
    insert_ingredient(ingredient)
    
    return make_succ_response({
        'id': ingredient.id,
        'name': ingredient.name,
        'category': ingredient.category,
        'updated_at': ingredient.updated_at.isoformat()
    })


@app.route('/api/ingredients/<ingredient_id>', methods=['PATCH'])
def update_ingredient_info(ingredient_id):
    """
    更新食材信息
    :param ingredient_id: 食材ID
    :return: 更新结果
    """
    params = request.get_json()
    
    # 检查食材是否存在
    existing_ingredient = query_ingredient_by_id(ingredient_id)
    if existing_ingredient is None:
        return make_err_response('食材不存在')
    
    # 更新食材信息
    success = update_ingredient(ingredient_id, params)
    if not success:
        return make_err_response('更新食材失败')
    
    # 返回更新后的食材信息
    updated_ingredient = query_ingredient_by_id(ingredient_id)
    return make_succ_response({
        'id': updated_ingredient.id,
        'name': updated_ingredient.name,
        'category': updated_ingredient.category,
        'updated_at': updated_ingredient.updated_at.isoformat()
    })


# ==================== 食材尝试记录接口 ====================
@app.route('/api/babies/<baby_id>/food-trials', methods=['POST'])
def create_food_trial(baby_id):
    """
    添加食材尝试记录
    :param baby_id: 宝宝ID
    :return: 记录信息
    """
    params = request.get_json()
    
    if 'ingredient_id' not in params or 'trial_date' not in params:
        return make_err_response('缺少必需参数')
    
    # 创建记录
    trial = FoodTrial()
    trial.id = str(uuid.uuid4())
    trial.baby_id = baby_id
    trial.ingredient_id = params['ingredient_id']
    trial.trial_date = datetime.strptime(params['trial_date'], '%Y-%m-%d').date()
    trial.trial_count = params.get('trial_count', 1)
    trial.is_allergic = params.get('is_allergic', False)
    trial.reaction_level = params.get('reaction_level', 'none')
    trial.notes = params.get('notes', '')
    trial.created_at = datetime.now()
    
    insert_food_trial(trial)
    
    return make_succ_response({
        'id': trial.id,
        'baby_id': trial.baby_id,
        'ingredient_id': trial.ingredient_id,
        'trial_date': trial.trial_date.isoformat(),
        'trial_count': trial.trial_count,
        'is_allergic': trial.is_allergic,
        'reaction_level': trial.reaction_level,
        'notes': trial.notes,
        'created_at': trial.created_at.isoformat()
    })


@app.route('/api/babies/<baby_id>/food-trials', methods=['GET'])
def get_food_trials(baby_id):
    """
    获取宝宝的食材尝试记录
    :param baby_id: 宝宝ID
    :return: 记录列表
    """
    trials = query_food_trials_by_baby(baby_id)
    
    trials_data = [{
        'id': trial.id,
        'baby_id': trial.baby_id,
        'ingredient_id': trial.ingredient_id,
        'trial_date': trial.trial_date.isoformat(),
        'trial_count': trial.trial_count,
        'is_allergic': trial.is_allergic,
        'reaction_level': trial.reaction_level,
        'notes': trial.notes,
        'created_at': trial.created_at.isoformat()
    } for trial in trials]
    
    return make_succ_response(trials_data)


# ==================== 食谱管理接口 ====================
@app.route('/api/recipes', methods=['POST'])
def create_recipe():
    """
    创建食谱
    :return: 食谱信息
    """
    params = request.get_json()
    
    required_fields = ['baby_id', 'recipe_date']
    for field in required_fields:
        if field not in params:
            return make_err_response(f'缺少必需参数: {field}')
    
    # 创建食谱
    recipe = Recipe()
    recipe.id = str(uuid.uuid4())
    recipe.baby_id = params['baby_id']
    recipe.recipe_date = datetime.strptime(params['recipe_date'], '%Y-%m-%d').date()
    recipe.created_by = params.get('created_by', None)
    recipe.auto_generated = params.get('auto_generated', True)
    recipe.notes = params.get('notes', '')
    recipe.created_at = datetime.now()
    
    insert_recipe(recipe)
    
    return make_succ_response({
        'id': recipe.id,
        'baby_id': recipe.baby_id,
        'recipe_date': recipe.recipe_date.isoformat(),
        'created_by': recipe.created_by,
        'auto_generated': recipe.auto_generated,
        'notes': recipe.notes,
        'created_at': recipe.created_at.isoformat()
    })


@app.route('/api/recipes', methods=['GET'])
def get_recipes():
    """
    查询食谱（按宝宝ID和日期）
    :return: 食谱信息
    """
    baby_id = request.args.get('baby_id')
    recipe_date = request.args.get('date')
    
    if not baby_id or not recipe_date:
        return make_err_response('缺少baby_id或date参数')
    
    recipe_date_obj = datetime.strptime(recipe_date, '%Y-%m-%d').date()
    recipe = query_recipe_by_baby_and_date(baby_id, recipe_date_obj)
    
    if recipe is None:
        return make_err_response('食谱不存在')
    
    # 获取食谱项
    items = query_recipe_items(recipe.id)
    items_data = [{
        'id': item.id,
        'meal_type': item.meal_type,
        'ingredients': item.ingredients,
        'instructions': item.instructions
    } for item in items]
    
    return make_succ_response({
        'id': recipe.id,
        'baby_id': recipe.baby_id,
        'recipe_date': recipe.recipe_date.isoformat(),
        'created_by': recipe.created_by,
        'auto_generated': recipe.auto_generated,
        'notes': recipe.notes,
        'items': items_data,
        'created_at': recipe.created_at.isoformat()
    })


@app.route('/api/babies/<baby_id>/recipes', methods=['GET'])
def get_baby_recipes(baby_id):
    """
    获取宝宝的全部食谱记录
    :param baby_id: 宝宝ID
    :return: 食谱列表
    """
    recipes = query_recipes_by_baby(baby_id)
    
    recipes_data = [{
        'id': recipe.id,
        'baby_id': recipe.baby_id,
        'recipe_date': recipe.recipe_date.isoformat(),
        'created_by': recipe.created_by,
        'auto_generated': recipe.auto_generated,
        'notes': recipe.notes,
        'created_at': recipe.created_at.isoformat()
    } for recipe in recipes]
    
    return make_succ_response(recipes_data)


@app.route('/api/recipes/<recipe_id>', methods=['PATCH'])
def update_recipe_info(recipe_id):
    """
    更新食谱备注
    :param recipe_id: 食谱ID
    :return: 更新结果
    """
    params = request.get_json()
    
    # 检查食谱是否存在
    existing_recipe = query_recipe_by_id(recipe_id)
    if existing_recipe is None:
        return make_err_response('食谱不存在')
    
    # 更新食谱
    success = update_recipe(recipe_id, params)
    if not success:
        return make_err_response('更新食谱失败')
    
    # 返回更新后的食谱信息
    updated_recipe = query_recipe_by_id(recipe_id)
    return make_succ_response({
        'id': updated_recipe.id,
        'notes': updated_recipe.notes
    })


@app.route('/api/recipes/<recipe_id>', methods=['DELETE'])
def delete_recipe_info(recipe_id):
    """
    删除食谱
    :param recipe_id: 食谱ID
    :return: 删除结果
    """
    success = delete_recipe(recipe_id)
    if not success:
        return make_err_response('食谱不存在或删除失败')
    
    return make_succ_empty_response()


# ==================== 食谱项接口 ====================
@app.route('/api/recipes/<recipe_id>/items', methods=['POST'])
def create_recipe_item(recipe_id):
    """
    添加食谱项（餐次）
    :param recipe_id: 食谱ID
    :return: 食谱项信息
    """
    params = request.get_json()
    
    if 'meal_type' not in params:
        return make_err_response('缺少meal_type参数')
    
    # 检查食谱是否存在
    recipe = query_recipe_by_id(recipe_id)
    if recipe is None:
        return make_err_response('食谱不存在')
    
    # 创建食谱项
    item = RecipeItem()
    item.id = str(uuid.uuid4())
    item.recipe_id = recipe_id
    item.meal_type = params['meal_type']
    item.ingredients = params.get('ingredients', [])
    item.instructions = params.get('instructions', '')
    item.created_at = datetime.now()
    
    insert_recipe_item(item)
    
    return make_succ_response({
        'id': item.id,
        'recipe_id': item.recipe_id,
        'meal_type': item.meal_type,
        'ingredients': item.ingredients,
        'instructions': item.instructions,
        'created_at': item.created_at.isoformat()
    })


@app.route('/api/recipes/<recipe_id>/items', methods=['GET'])
def get_recipe_items(recipe_id):
    """
    获取食谱下的所有餐次
    :param recipe_id: 食谱ID
    :return: 餐次列表
    """
    items = query_recipe_items(recipe_id)
    
    items_data = [{
        'id': item.id,
        'recipe_id': item.recipe_id,
        'meal_type': item.meal_type,
        'ingredients': item.ingredients,
        'instructions': item.instructions,
        'created_at': item.created_at.isoformat()
    } for item in items]
    
    return make_succ_response(items_data)


@app.route('/api/recipe-items/<item_id>', methods=['PATCH'])
def update_recipe_item_info(item_id):
    """
    修改餐次内容
    :param item_id: 食谱项ID
    :return: 更新结果
    """
    params = request.get_json()
    
    # 检查食谱项是否存在
    existing_item = query_recipe_item_by_id(item_id)
    if existing_item is None:
        return make_err_response('食谱项不存在')
    
    # 更新食谱项
    success = update_recipe_item(item_id, params)
    if not success:
        return make_err_response('更新食谱项失败')
    
    # 返回更新后的食谱项信息
    updated_item = query_recipe_item_by_id(item_id)
    return make_succ_response({
        'id': updated_item.id,
        'recipe_id': updated_item.recipe_id,
        'meal_type': updated_item.meal_type,
        'ingredients': updated_item.ingredients,
        'instructions': updated_item.instructions
    })


@app.route('/api/recipe-items/<item_id>', methods=['DELETE'])
def delete_recipe_item_info(item_id):
    """
    删除餐次
    :param item_id: 食谱项ID
    :return: 删除结果
    """
    success = delete_recipe_item(item_id)
    if not success:
        return make_err_response('食谱项不存在或删除失败')
    
    return make_succ_empty_response()


# ==================== 特殊事件接口 ====================
@app.route('/api/events', methods=['POST'])
def create_event():
    """
    添加事件
    :return: 事件信息
    """
    params = request.get_json()
    
    required_fields = ['baby_id', 'event_type', 'start_date']
    for field in required_fields:
        if field not in params:
            return make_err_response(f'缺少必需参数: {field}')
    
    # 创建事件
    event = Event()
    event.id = str(uuid.uuid4())
    event.baby_id = params['baby_id']
    event.event_type = params['event_type']
    event.start_date = datetime.strptime(params['start_date'], '%Y-%m-%d').date()
    event.end_date = datetime.strptime(params['end_date'], '%Y-%m-%d').date() if 'end_date' in params else None
    event.description = params.get('description', '')
    event.created_at = datetime.now()
    
    insert_event(event)
    
    return make_succ_response({
        'id': event.id,
        'baby_id': event.baby_id,
        'event_type': event.event_type,
        'start_date': event.start_date.isoformat(),
        'end_date': event.end_date.isoformat() if event.end_date else None,
        'description': event.description,
        'created_at': event.created_at.isoformat()
    })


@app.route('/api/babies/<baby_id>/events', methods=['GET'])
def get_baby_events(baby_id):
    """
    查看宝宝的所有事件
    :param baby_id: 宝宝ID
    :return: 事件列表
    """
    events = query_events_by_baby(baby_id)
    
    events_data = [{
        'id': event.id,
        'baby_id': event.baby_id,
        'event_type': event.event_type,
        'start_date': event.start_date.isoformat(),
        'end_date': event.end_date.isoformat() if event.end_date else None,
        'description': event.description,
        'created_at': event.created_at.isoformat()
    } for event in events]
    
    return make_succ_response(events_data)


@app.route('/api/events/<event_id>', methods=['PATCH'])
def update_event_info(event_id):
    """
    修改事件信息
    :param event_id: 事件ID
    :return: 更新结果
    """
    params = request.get_json()
    
    # 检查事件是否存在
    existing_event = query_event_by_id(event_id)
    if existing_event is None:
        return make_err_response('事件不存在')
    
    # 处理日期格式
    if 'start_date' in params:
        params['start_date'] = datetime.strptime(params['start_date'], '%Y-%m-%d').date()
    if 'end_date' in params:
        params['end_date'] = datetime.strptime(params['end_date'], '%Y-%m-%d').date()
    
    # 更新事件
    success = update_event(event_id, params)
    if not success:
        return make_err_response('更新事件失败')
    
    # 返回更新后的事件信息
    updated_event = query_event_by_id(event_id)
    return make_succ_response({
        'id': updated_event.id,
        'baby_id': updated_event.baby_id,
        'event_type': updated_event.event_type,
        'start_date': updated_event.start_date.isoformat(),
        'end_date': updated_event.end_date.isoformat() if updated_event.end_date else None,
        'description': updated_event.description
    })


@app.route('/api/events/<event_id>', methods=['DELETE'])
def delete_event_info(event_id):
    """
    删除事件
    :param event_id: 事件ID
    :return: 删除结果
    """
    success = delete_event(event_id)
    if not success:
        return make_err_response('事件不存在或删除失败')
    
    return make_succ_empty_response()


# ==================== 通知接口 ====================
@app.route('/api/users/<user_id>/notifications', methods=['GET'])
def get_user_notifications(user_id):
    """
    获取用户通知列表
    :param user_id: 用户ID
    :return: 通知列表
    """
    is_read = request.args.get('is_read', None)
    if is_read is not None:
        is_read = is_read.lower() == 'true'
    
    notifications = query_notifications_by_user(user_id, is_read)
    
    notifications_data = [{
        'id': notification.id,
        'user_id': notification.user_id,
        'type': notification.type,
        'title': notification.title,
        'message': notification.message,
        'is_read': notification.is_read,
        'created_at': notification.created_at.isoformat()
    } for notification in notifications]
    
    return make_succ_response(notifications_data)


@app.route('/api/notifications/<notification_id>/read', methods=['PATCH'])
def mark_notification_as_read(notification_id):
    """
    标记通知为已读
    :param notification_id: 通知ID
    :return: 更新结果
    """
    success = mark_notification_read(notification_id)
    if not success:
        return make_err_response('通知不存在或标记失败')
    
    return make_succ_empty_response()


@app.route('/api/users/<user_id>/notifications/read-all', methods=['PATCH'])
def mark_all_notifications_as_read(user_id):
    """
    标记用户所有通知为已读
    :param user_id: 用户ID
    :return: 更新结果
    """
    success = mark_all_notifications_read(user_id)
    if not success:
        return make_err_response('标记失败')
    
    return make_succ_empty_response()
