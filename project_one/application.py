import redis

from flask import Flask, render_template
from flask_wtf.csrf import CSRFProtect
from flask_session import Session

from configs import *
from views_user import app_user
from views_news import app_news
from views_admin import app_admin

def create_application():
    app = Flask(__name__)
    logger_console.info("start to load config")
    logger_file.info("start to load config")
    app.config.from_object(DevelopConfig)

    CSRFProtect(app)

    Session(app)

    logger_console.info("start to register blueprint")
    logger_file.info("start to register blueprint")
    app.register_blueprint(app_user, url_prefix='/user')
    app.register_blueprint(app_news)
    app.register_blueprint(app_admin, url_prefix='/admin')

    redis_host = DevelopConfig.REDIS_HOST
    redis_port = DevelopConfig.REDIS_PORT
    redis_db = DevelopConfig.REDIS_DB
    app.redis_client = redis.StrictRedis(host=redis_host, port=redis_port, db=redis_db)

    @app.errorhandler(404)
    def handle404(e):
        return render_template('news/404.html')

    return app

