from datetime import datetime
from flask import request
from run import app
from wxcloudrun.dao import delete_counterbyid, query_counterbyid, insert_counter, update_counterbyid, query_user_by_uid, query_all_users, insert_user, update_user_by_uid, delete_user_by_uid
from wxcloudrun.model import Counters, User
from wxcloudrun.response import make_succ_empty_response, make_succ_response, make_err_response



@app.route('/api/count', methods=['POST'])
def count():
    """
    :return:计数结果/清除结果
    """

    # 获取请求体参数
    params = request.get_json()

    # 检查action参数
    if 'action' not in params:
        return make_err_response('缺少action参数')

    # 按照不同的action的值，进行不同的操作
    action = params['action']

    # 执行自增操作
    if action == 'inc':
        counter = query_counterbyid(1)
        if counter is None:
            counter = Counters()
            counter.id = 1
            counter.count = 1
            counter.created_at = datetime.now()
            counter.updated_at = datetime.now()
            insert_counter(counter)
        else:
            counter.id = 1
            counter.count += 1
            counter.updated_at = datetime.now()
            update_counterbyid(counter)
        return make_succ_response(counter.count)

    # 执行清0操作
    elif action == 'clear':
        delete_counterbyid(1)
        return make_succ_empty_response()

    # action参数错误
    else:
        return make_err_response('action参数错误')


@app.route('/api/count', methods=['GET'])
def get_count():
    """
    :return: 计数的值
    """
    counter = Counters.query.filter(Counters.id == 1).first()
    return make_succ_response(0) if counter is None else make_succ_response(counter.count)


# ==================== 用户相关接口 ====================

@app.route('/api/users', methods=['POST'])
def create_user():
    """
    创建用户
    :return: 创建结果
    """
    params = request.get_json()
    
    # 检查必需参数
    if 'uid' not in params:
        return make_err_response('缺少uid参数')
    if 'nickname' not in params:
        return make_err_response('缺少nickname参数')
    
    uid = params['uid']
    nickname = params['nickname']
    avatar = params.get('avatar', '')  # 头像可选
    
    # 检查用户是否已存在
    existing_user = query_user_by_uid(uid)
    if existing_user is not None:
        return make_err_response('用户已存在')
    
    # 创建新用户
    user = User()
    user.uid = uid
    user.nickname = nickname
    user.avatar = avatar
    user.created_at = datetime.now()
    
    insert_user(user)
    return make_succ_response({
        'uid': user.uid,
        'nickname': user.nickname,
        'avatar': user.avatar,
        'createdAt': user.created_at.isoformat()
    })


@app.route('/api/users/<uid>', methods=['GET'])
def get_user(uid):
    """
    根据UID获取用户信息
    :param uid: 用户唯一标识
    :return: 用户信息
    """
    user = query_user_by_uid(uid)
    if user is None:
        return make_err_response('用户不存在')
    
    return make_succ_response({
        'uid': user.uid,
        'nickname': user.nickname,
        'avatar': user.avatar,
        'createdAt': user.created_at.isoformat()
    })


@app.route('/api/users/<uid>', methods=['PUT'])
def update_user(uid):
    """
    更新用户信息
    :param uid: 用户唯一标识
    :return: 更新结果
    """
    params = request.get_json()
    
    # 检查用户是否存在
    existing_user = query_user_by_uid(uid)
    if existing_user is None:
        return make_err_response('用户不存在')
    
    # 更新用户信息
    user = User()
    user.uid = uid
    user.nickname = params.get('nickname', existing_user.nickname)
    user.avatar = params.get('avatar', existing_user.avatar)
    
    success = update_user_by_uid(user)
    if not success:
        return make_err_response('更新用户失败')
    
    # 返回更新后的用户信息
    updated_user = query_user_by_uid(uid)
    return make_succ_response({
        'uid': updated_user.uid,
        'nickname': updated_user.nickname,
        'avatar': updated_user.avatar,
        'createdAt': updated_user.created_at.isoformat()
    })


@app.route('/api/users/<uid>', methods=['DELETE'])
def delete_user(uid):
    """
    删除用户
    :param uid: 用户唯一标识
    :return: 删除结果
    """
    success = delete_user_by_uid(uid)
    if not success:
        return make_err_response('用户不存在或删除失败')
    
    return make_succ_empty_response()
