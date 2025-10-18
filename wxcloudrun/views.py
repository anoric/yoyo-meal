from datetime import datetime
from flask import request
from run import app
from wxcloudrun.dao import delete_counterbyid, query_counterbyid, insert_counter, update_counterbyid, query_user_by_uid, query_user_by_openid, insert_user, update_user_by_uid, delete_user_by_uid
from wxcloudrun.model import Counters, User
from wxcloudrun.response import make_succ_empty_response, make_succ_response, make_err_response
import requests
import config



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
        
        response = requests.get(wechat_url, params=wechat_params, timeout=10)
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
                'uid': existing_user.uid,
                'nickname': existing_user.nickname,
                'avatar': existing_user.avatar,
                'createdAt': existing_user.created_at.isoformat(),
                'isNewUser': False
            }
        else:
            # 用户不存在，创建新用户
            user = User()
            user.uid = openid  # 使用openid作为用户唯一标识
            user.nickname = f'微信用户_{openid[-6:]}'  # 默认昵称
            user.avatar = ''  # 默认头像为空
            user.created_at = datetime.now()
            
            insert_user(user)
            
            user_data = {
                'uid': user.uid,
                'nickname': user.nickname,
                'avatar': user.avatar,
                'createdAt': user.created_at.isoformat(),
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
