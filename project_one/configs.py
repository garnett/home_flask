# -*- coding:utf-8 -*-
import redis

import os

import logging
from logging.config import fileConfig

log_config_path = os.path.join(os.path.dirname(__file__), "log.conf")
fileConfig(log_config_path)
logger_console = logging.getLogger(name="root")
logger_file = logging.getLogger(name="log_flask")

class BaseConfig():
    DEBUG = True


class DevelopConfig(BaseConfig):
    DEBUG = False
    port = 5005
    SQLALCHEMY_DATABASE_URI = 'mysql://root:1347699lyq@localhost:3306/flask_app'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    REDIS_HOST = 'localhost'
    REDIS_PORT = 6379
    REDIS_DB = 2

    SECRET_KEY = 'celtics'

    SESSION_TYPE = "redis"
    SESSION_USE_SIGNER = True
    SESSION_REDIS = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)

    PERMANENT_SESSION_LIFETIME = 60 * 60 * 24

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    # 七牛云配置
    QINIU_AK = 'dfSC-vzHZ5vHHhqEZX16oCH7wHMzgWm7bHJb7lLP'
    QINIU_SK = 'DWgsC5GiknRUZ5Z1-HttMrEWf-DU2dylJK0U0iLc'
    QINIU_URL = 'http://qflgjl93y.hn-bkt.clouddn.com/'
    QINIU_SPACE = 'mamba-forever'