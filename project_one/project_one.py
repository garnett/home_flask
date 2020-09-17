import pymysql
pymysql.install_as_MySQLdb()

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# print(sys.path)

# import platform
# windows_log_path = 'C:project_log/flask_app_logs'
# linux_log_path = 'var/logs/flask_app_logs'
# # print('=========================', platform.system())
#
# if platform.system()=='Windows':
#     if not os.path.exists(windows_log_path):
#         print(windows_log_path)
#         os.makedirs(windows_log_path)
# elif platform.system()=='Linux':
#     if not os.path.exists(linux_log_path):
#         os.makedirs(linux_log_path)
# else:
#     pass

from flask import Flask
from flask_script import Manager
from flask_migrate import MigrateCommand, Migrate

from application import create_application
from models import db
from self_commands import *

app = create_application()

manager = Manager(app)

# 实例化SQLAlchemy对象
db.init_app(app)

# 数据库迁移命令绑定
Migrate(app, db)
manager.add_command('db', MigrateCommand)

manager.add_command('administrator', CreateAdmin)
manager.add_command('createhour', CreateHour)

if __name__ == '__main__':
    # app.run()
    manager.run()