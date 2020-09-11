from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

from configs import DevelopConfig

db = SQLAlchemy()


class BaseModel():
    create_time = db.Column(db.DateTime, default=datetime.now)
    update_time = db.Column(db.DateTime, default=datetime.now)
    is_delete = db.Column(db.Boolean, default=False)


# 用户收藏新闻关系表
tb_user_news = db.Table(
    'tb_user_news',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('news_id', db.Integer, db.ForeignKey('news.id'), primary_key=True)
)


# 用户关注其他用户表
tb_user_follow = db.Table(
    'tb_user_follow',
    db.Column('origin_user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('follow_user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True)
)


# 用户点赞评论表
tb_user_like = db.Table(
    'tb_user_like_comments',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('comment_id', db.Integer, db.ForeignKey('news_comment.id'), primary_key=True)
)


class NewsCategory(db.Model, BaseModel):
    __tablename__ = 'news_category'
    id = db.Column(db.Integer, primary_key= True)
    name = db.Column(db.String(64))
    news = db.relationship('News', backref='category', lazy='dynamic')


class News(db.Model, BaseModel):
    __tablename__= 'news'
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('news_category.id'))
    pic = db.Column(db.String(64))
    title = db.Column(db.String(32))
    summary = db.Column(db.String(200))
    content = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    click_count = db.Column(db.Integer, default=0)
    source = db.Column(db.String(32), default='')
    comment_count = db.Column(db.Integer, default=0)
    status = db.Column(db.SmallInteger, default=1)
    reason = db.Column(db.String(100), default='')
    comments = db.relationship('NewsComment', backref='news', lazy='dynamic', order_by='NewsComment.id.desc()')
    # user_collect = db.relationship('User', secondary=tb_user_news, lazy='dynamic')

    @property
    def pic_url(self):
        return DevelopConfig.QINIU_URL + self.pic


class User(db.Model, BaseModel):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    avatar = db.Column(db.String(64), default='user_pic.png')
    nick_name = db.Column(db.String(32))
    signature = db.Column(db.String(128), default="这个家伙很懒，什么都没有留下！")
    public_count = db.Column(db.Integer, default=0)
    follow_count = db.Column(db.Integer, default=0)
    mobile = db.Column(db.String(11))
    password_hash = db.Column(db.String(200))
    gender = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)

    news = db.relationship('News', backref='user', lazy='dynamic')
    comments = db.relationship('NewsComment', backref='user', lazy='dynamic')
    # 新闻收藏 多对多
    news_collect = db.relationship('News', secondary=tb_user_news, lazy='dynamic', backref='collect_users')
    # 用户关注，自关联多对多
    follow_user = db.relationship('User', secondary=tb_user_follow, lazy='dynamic',
                                  primaryjoin=id == tb_user_follow.c.origin_user_id,
                                  secondaryjoin=id == tb_user_follow.c.follow_user_id,
                                  backref = db.backref('follow_by_user', lazy='dynamic'))

    like_comments = db.relationship('NewsComment', secondary=tb_user_like, lazy='dynamic', backref='like_by_users')

    @property
    def password(self):
        pass

    @password.setter
    def password(self, pwd):
        self.password_hash = generate_password_hash(pwd)

    def check_pwd(self, pwd):
        return check_password_hash(self.password_hash, pwd)

    @property
    def avatar_url(self):
        return DevelopConfig.QINIU_URL + self.avatar


class NewsComment(db.Model, BaseModel):
    __tablename__ = 'news_comment'
    id = db.Column(db.Integer, primary_key=True)
    news_id = db.Column(db.Integer, db.ForeignKey('news.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    like_count = db.Column(db.Integer, default=0)
    comment_id = db.Column(db.Integer, db.ForeignKey('news_comment.id'))
    msg = db.Column(db.String(200))
    comments = db.relationship('NewsComment', lazy='dynamic')