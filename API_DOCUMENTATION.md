# 宝宝辅食管理系统 API 文档

## 基础信息

- 基础 URL: `http://your-domain.com/api`
- 所有请求和响应均使用 JSON 格式
- 统一响应格式：
  - 成功: `{"code": 0, "data": {...}}`
  - 失败: `{"code": -1, "errorMsg": "错误信息"}`

## 一、认证接口

### 1. 微信小程序登录

```
POST /api/auth/login
```

**请求参数：**

```json
{
  "code": "微信登录code"
}
```

**响应：**

```json
{
  "code": 0,
  "data": {
    "user": {
      "id": "用户ID",
      "nickname": "用户昵称",
      "avatar_url": "头像URL",
      "created_at": "2025-10-19T01:00:00",
      "isNewUser": false
    },
    "sessionKey": "session_key",
    "unionid": "unionid"
  }
}
```

## 二、用户接口

### 1. 创建用户

```
POST /api/users
```

**请求参数：**

```json
{
  "nickname": "妈妈",
  "avatar_url": "https://cdn.app/avatar1.png"
}
```

### 2. 获取用户信息

```
GET /api/users/{user_id}
```

### 3. 更新用户信息

```
PATCH /api/users/{user_id}
```

**请求参数：**

```json
{
  "nickname": "新昵称",
  "avatar_url": "新头像URL"
}
```

### 4. 删除用户

```
DELETE /api/users/{user_id}
```

## 三、家庭管理接口

### 1. 创建家庭

```
POST /api/families
```

**请求参数：**

```json
{
  "name": "小鱼儿之家",
  "created_by": "用户ID"
}
```

### 2. 获取家庭信息

```
GET /api/families/{family_id}
```

### 3. 添加家庭成员

```
POST /api/families/{family_id}/members
```

**请求参数：**

```json
{
  "user_id": "用户ID",
  "role": "member" // 可选: admin 或 member
}
```

### 4. 获取家庭成员列表

```
GET /api/families/{family_id}/members
```

### 5. 获取用户所属家庭列表

```
GET /api/users/{user_id}/families
```

## 四、宝宝管理接口

### 1. 添加宝宝

```
POST /api/babies
```

**请求参数：**

```json
{
  "nickname": "小鱼儿",
  "gender": "F", // M=男, F=女
  "birth_date": "2024-05-01",
  "created_by": "用户ID", // 必需
  "family_id": "家庭ID", // 可选，不提供时自动创建或使用用户现有家庭
  "avatar_url": "头像URL",
  "avoid_ingredients": ["egg", "peanut"]
}
```

**说明：**

- 如果不提供 `family_id`：
  - 若用户已有家庭，将宝宝添加到用户的第一个家庭
  - 若用户没有家庭，自动创建一个名为 `{宝宝昵称}的家庭` 的新家庭，并将用户设为管理员

### 2. 获取宝宝信息

```
GET /api/babies/{baby_id}
```

### 3. 获取家庭下所有宝宝

```
GET /api/families/{family_id}/babies
```

### 4. 更新宝宝信息

```
PATCH /api/babies/{baby_id}
```

### 5. 删除宝宝

```
DELETE /api/babies/{baby_id}
```

## 五、食材库接口

### 1. 获取食材列表（分页）

```
GET /api/ingredients?page=1&page_size=20&category=蔬菜
```

**查询参数：**

- `page`: 页码（默认 1）
- `page_size`: 每页数量（默认 20）
- `category`: 分类筛选（可选）

### 2. 获取单个食材

```
GET /api/ingredients/{ingredient_id}
```

### 3. 添加食材

```
POST /api/ingredients
```

**请求参数：**

```json
{
  "name": "胡萝卜",
  "category": "蔬菜",
  "image_url": "图片URL",
  "risk_level": "low", // low, medium, high
  "nutrients": {
    "vitaminA": 25,
    "fiber": 1.2
  },
  "summary": "富含维生素A",
  "description": "详细描述",
  "suitable_month_from": 6,
  "suitable_month_to": 36
}
```

### 4. 更新食材信息

```
PATCH /api/ingredients/{ingredient_id}
```

## 六、食材尝试记录接口

### 1. 添加尝试记录

```
POST /api/babies/{baby_id}/food-trials
```

**请求参数：**

```json
{
  "ingredient_id": "食材ID",
  "trial_date": "2025-10-19",
  "trial_count": 1,
  "is_allergic": false,
  "reaction_level": "none", // none, mild, moderate, severe
  "notes": "备注"
}
```

### 2. 获取宝宝的尝试记录

```
GET /api/babies/{baby_id}/food-trials
```

## 七、食谱管理接口

### 1. 创建食谱

```
POST /api/recipes
```

**请求参数：**

```json
{
  "baby_id": "宝宝ID",
  "recipe_date": "2025-10-19",
  "created_by": "用户ID",
  "auto_generated": true,
  "notes": "备注"
}
```

### 2. 查询食谱（按日期）

```
GET /api/recipes?baby_id={baby_id}&date=2025-10-19
```

### 3. 获取宝宝所有食谱

```
GET /api/babies/{baby_id}/recipes
```

### 4. 更新食谱

```
PATCH /api/recipes/{recipe_id}
```

**请求参数：**

```json
{
  "notes": "更新的备注"
}
```

### 5. 删除食谱

```
DELETE /api/recipes/{recipe_id}
```

## 八、食谱项（餐次）接口

### 1. 添加餐次

```
POST /api/recipes/{recipe_id}/items
```

**请求参数：**

```json
{
  "meal_type": "lunch", // breakfast, morning_snack, lunch, afternoon_snack, dinner
  "ingredients": [
    { "id": "食材ID1", "name": "胡萝卜" },
    { "id": "食材ID2", "name": "苹果" }
  ],
  "instructions": "蒸熟后搅拌混合"
}
```

### 2. 获取食谱的所有餐次

```
GET /api/recipes/{recipe_id}/items
```

### 3. 修改餐次

```
PATCH /api/recipe-items/{item_id}
```

### 4. 删除餐次

```
DELETE /api/recipe-items/{item_id}
```

## 九、特殊事件接口

### 1. 添加事件

```
POST /api/events
```

**请求参数：**

```json
{
  "baby_id": "宝宝ID",
  "event_type": "vaccine", // illness, vaccine, other
  "start_date": "2025-10-18",
  "end_date": "2025-10-19",
  "description": "接种百白破疫苗"
}
```

### 2. 获取宝宝的所有事件

```
GET /api/babies/{baby_id}/events
```

### 3. 修改事件

```
PATCH /api/events/{event_id}
```

### 4. 删除事件

```
DELETE /api/events/{event_id}
```

## 十、通知接口

### 1. 获取用户通知列表

```
GET /api/users/{user_id}/notifications?is_read=false
```

**查询参数：**

- `is_read`: 筛选已读/未读（可选）

### 2. 标记通知为已读

```
PATCH /api/notifications/{notification_id}/read
```

### 3. 标记所有通知为已读

```
PATCH /api/users/{user_id}/notifications/read-all
```

## 项目结构

```
wxcloudrun/
├── __init__.py          # Flask应用初始化，数据库配置
├── views.py             # 所有API路由定义
├── tables.py            # 数据模型定义
├── response.py          # 统一响应格式
├── func_user.py         # 用户相关数据库操作
├── func_family.py       # 家庭管理数据库操作
├── func_baby.py         # 宝宝管理数据库操作
├── func_ingredient.py   # 食材相关数据库操作
├── func_recipe.py       # 食谱相关数据库操作
└── func_event.py        # 事件和通知数据库操作
```

## 数据库配置

在 `config.py` 中配置数据库连接信息：

```python
username = os.environ.get("MYSQL_USERNAME", 'root')
password = os.environ.get("MYSQL_PASSWORD", 'root')
db_address = os.environ.get("MYSQL_ADDRESS", '127.0.0.1:3306')
```

数据库名称：`baby_meal`

## 运行项目

```bash
python run.py
```

服务将在配置的端口上启动（默认通常是 5000）。
