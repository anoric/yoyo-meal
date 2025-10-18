import os

# 是否开启debug模式
DEBUG = True

# 读取数据库环境变量
username = os.environ.get("MYSQL_USERNAME", 'root')
password = os.environ.get("MYSQL_PASSWORD", 'root')
db_address = os.environ.get("MYSQL_ADDRESS", '127.0.0.1:3306')

# 微信小程序配置 
WECHAT_APPID = os.environ.get("WECHAT_APPID", 'wx1cf97f5a388d7690')
WECHAT_SECRET = os.environ.get("WECHAT_SECRET", 'b9a3632f9516137d5ed6fd0a3722b4a2')
