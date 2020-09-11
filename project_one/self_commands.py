import random

from datetime import datetime
from flask import current_app

from flask_script.commands import Command
from models import *


class CreateAdmin(Command):
    def run(self):
        mobile = input('please input phone number:')
        nick = input('please input nick name:')
        pwd = input('please input password')

        if_exist = User.query.filter_by(mobile=mobile).count()
        if if_exist > 0:
            print("该号码已被注册！")
            return

        user_admin = User()
        user_admin.mobile = mobile
        user_admin.password = pwd
        user_admin.nick_name = nick
        user_admin.is_admin = 1

        db.session.add(user_admin)
        db.session.commit()
        print("create administrator success!")


class CreateHour(Command):
    def run(self):
        """
        login_2020_09_02:{08:15: 211, 09:15: 199,}
        :return:
        """
        now_time = datetime.now()
        redis_key = "login_%d_%02d_%02d" % (now_time.year, now_time.month, now_time.day)
        for i in range(8, 20):
            key = "%02d:15" % i
            value = random.randint(100, 800)
            current_app.redis_client.hset(redis_key, key, value)
