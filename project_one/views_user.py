import random

from flask import Blueprint, render_template, request, jsonify, make_response, session, redirect,current_app
from utils.captcha.captcha import captcha
from utils.verify_params import *
from utils.send_message_by_ytx import send_message
from models import *
from configs import logger_console, logger_file
from utils.decorations import login_required, login_require, LoginRequire
from utils.upload_pic_qiniu import upload_pic_by_qiniu
from utils.get_redis_hour_key import *

app_user = Blueprint('app_user', __name__)


@app_user.route('/image_yzm')
def image_yzm():
    name, yzm, buffer = captcha.generate_captcha()

    session["image_yzm"] = yzm

    return make_response(buffer, 'image/png')


@app_user.route('/sms_yzm')
def sms_yzm():
    phone = request.args.get("mobile")
    image_code = request.args.get("image_yzm")

    if not verify_phone_number(phone):
        return jsonify(result=3)

    if_exist = User.query.filter_by(mobile=phone).count()
    if if_exist:
        return jsonify(result=0, message="该手机号用户已存在")

    if session["image_yzm"] != image_code:
        return jsonify(result=1)

    random_yzm = random.randint(1000, 9999)
    session['sms_yzm'] = random_yzm
    print(random_yzm)

    ytx_res = send_message(phone, str(random_yzm))
    print(ytx_res)

    return jsonify(result=2, message="请查收短信！")


@app_user.route('/register', methods=['POST'])
def register():
    request_params = request.form
    phone = request_params.get("mobile")
    image_code = request_params.get("image_yzm")
    sms_code = request_params.get("sms_yzm")
    pwd = request_params.get("pwd")

    if not all([phone, image_code, sms_code, pwd]):
        return jsonify(result=0, message="注册参数填写不完整！")

    if not verify_phone_number(phone):
        return jsonify(result=2, message="该手机号不合法！")

    if session["image_yzm"] != image_code:
        return jsonify(result=3, message="图片验证码错误！")

    if str(session["sms_yzm"]) != sms_code:
        return jsonify(result=1, message="短信验证码错误！")

    if not verify_pwd(pwd):
        return jsonify(result=5, message="密码安全性不足！")

    if_exist = User.query.filter_by(mobile=phone).count()
    if if_exist:
        return jsonify(result=4, message="该手机号用户已存在")

    cur_user = User()
    cur_user.mobile = phone
    cur_user.password = pwd
    cur_user.nick_name = phone

    try:
        db.session.add(cur_user)
        db.session.commit()
    except Exception as e:
        logger_console.error(str(e))
        logger_file.error(str(e))
        return jsonify(result=6, message="服务器超时！")

    return jsonify(result=7, message="注册成功！")


@app_user.route('/login', methods=["POST"])
def login():
    request_data = request.form
    phone = request_data.get("mobile")
    password = request_data.get("pwd")

    if not all([phone, password]):
        return jsonify(result=1, message="请输入用户名和密码！")

    if not verify_phone_number(phone):
        return jsonify(result=2, message="手机号不合法！")

    if_exist = User.query.filter_by(mobile=phone).first()
    if not if_exist:
        return jsonify(result=4, message="该手机号用户不存在!")

    if not if_exist.check_pwd(password):
        return jsonify(result=5, message="用户名或密码错误！")

    session["user_id"] = if_exist.id

    redis_key = generate_hour_key()
    hour_key = generate_every_hour_new()
    if_day_user = current_app.redis_client.hkeys(redis_key)
    if not if_day_user:
        for i in range(8, 20):
            key = "%02d:15" % i
            current_app.redis_client.hset(redis_key, key, 0)
    # if_hour_user = current_app.redis_client.hget(redis_key, hour_key)
    # if if_hour_user:
    hour_val = int(current_app.redis_client.hget(redis_key, hour_key)) + 1
    # else:
    #     current_app.redis_client.hset(redis_key, hour_key, 1)
    #     hour_val = 1
    current_app.redis_client.hset(redis_key, hour_key, hour_val)

    return jsonify(result=6, message="登录成功！", avatar=if_exist.avatar_url, nick_name=if_exist.nick_name)


@app_user.route('/logout', methods=["POST"])
def logout():
    session.pop("user_id")
    return jsonify(result=1, message="退出成功！")


@app_user.route('/')
@LoginRequire(None)
def index():
    user_id = session.get("user_id")
    user = User.query.get(user_id)
    return render_template('news/user.html', web_name="用户中心", user=user)



@app_user.route('/<users_id>')
@LoginRequire(None)
def other_user(users_id):
    is_my_follow = 0
    user_id = session.get("user_id")
    user = User.query.get(user_id)

    user_other = User.query.get(int(users_id))

    if user_other in user.follow_user:
        is_my_follow=1
    return render_template(
        'news/other.html',
        user=user, user_other=user_other,
        is_my_follow=is_my_follow
    )


@app_user.route('/base', methods=["GET", "POST"])
@login_required
def user_base_info():
    user_id = session.get("user_id")
    user = User.query.get(user_id)
    if request.method == "GET":
        return render_template('news/user_base_info.html', user=user)
    elif request.method == "POST":
        req_params = request.form
        sig = req_params.get("signature")
        nick = req_params.get("nick_name")
        gender = req_params.get("gender")

        user.signature = sig
        user.nick_name = nick
        user.gender = 1 if gender == 'true' else 0

        db.session.add(user)
        db.session.commit()

        return jsonify(result=1, signature=sig, nick_name=nick, message='modify information success!')
    else:
        return jsonify(result=0, message="request method does not support!")


@app_user.route('/picture', methods=["GET", "POST"])
@login_required
def use_picture_head():
    user_id = session.get("user_id")
    user = User.query.get(user_id)
    if request.method == "GET":
        return render_template('news/user_pic_info.html', user=user)
    elif request.method == 'POST':
        file_pic = request.files.get('avatar')
        print(file_pic)
        print(type(file_pic))
        try:
            ret = upload_pic_by_qiniu(file_pic)
        except Exception as e:
            logger_console.error("upload picture failed because %s" %str(e))
            logger_file.error("upload picture failed because %s" %str(e))
            return jsonify(result=0, message="仅支持png,jpeg格式的图片！")
        user.avatar = ret
        try:
            db.session.commit()
        except Exception as e:
            logger_console.error("upload picture failed because %s" % str(e))
            logger_file.error("upload picture failed because %s" % str(e))
            return jsonify(result=0, message="连接超时，请重试！")
        return jsonify(result=1, pic_url=user.avatar_url, message='save avatar success!')


@app_user.route('/follow', methods=["GET"])
@login_required
def use_follow_info():
    user_id = session.get("user_id")
    user = User.query.get(user_id)
    cur_page = request.args.get('page', 1)
    per_page_num = request.args.get('number', 1)
    pagination = user.follow_user.paginate(int(cur_page), int(per_page_num), False)
    follow_user_list = pagination.items
    total_page = pagination.pages
    if request.method == "GET":
        return render_template('news/user_follow.html', page=cur_page, follow_list=follow_user_list, total_page=total_page)


@app_user.route('/news_list', methods=["GET"])
@login_required
def user_news():
    user_id = session.get("user_id")
    user = User.query.get(user_id)
    cur_page = request.args.get('page', 1)
    per_page_num = request.args.get('number', 1)
    user_news_list_obj = user.news.order_by(News.id.desc()).paginate(int(cur_page), int(per_page_num), False)
    user_news_list = user_news_list_obj.items
    total_page = user_news_list_obj.pages
    return render_template('news/user_news_list.html', page=cur_page, news_list=user_news_list, total_page=total_page)


@app_user.route('/modify/pwd', methods=["GET", "POST"])
@login_required
def modify_pwd():
    user_id = session.get("user_id")
    user = User.query.get(user_id)
    message = '密码修改成功！'
    result = 1
    if request.method == 'GET':
        return render_template('news/user_pass_info.html', user=user)
    elif request.method == 'POST':
        req_params = request.form
        old_pwd = req_params.get("old_pwd")
        new_pwd = req_params.get('new_pwd')
        again_pwd = req_params.get("again")
        if not all([old_pwd, new_pwd, again_pwd]):
            message = "参数不完整！"
            result = 0
            return jsonify(result=result, message=message)
        if not user.check_pwd(old_pwd):
            message = "密码错误！"
            result = 0
            return jsonify(result=result, message=message)
        if not verify_pwd(new_pwd):
            message = "密码安全性不足！"
            result = 0
            return jsonify(result=result, message=message)
        if new_pwd != again_pwd:
            message = "确认密码不一致！"
            result = 0
            return jsonify(result=result, message=message)
        if result:
            user.password = new_pwd
            db.session.commit()
        return jsonify(result=result, message=message)
    else:
        return jsonify(result=2, message="q请求方式不允许！")


@app_user.route('/collect/news', methods=["GET"])
@login_required
def user_collect_news():
    user_id = session.get("user_id")
    user = User.query.get(user_id)
    cur_page = request.args.get('page', 1)
    per_page_num = request.args.get('number', 1)
    pagination = user.news_collect.order_by(News.id.desc()).paginate(int(cur_page), int(per_page_num), False)
    news_list = pagination.items
    total_page = pagination.pages
    return render_template('news/user_collection.html', page=cur_page, total_page=total_page, news_list=news_list)


@app_user.route('/publish/news', methods=["GET", "POST"])
@LoginRequire(None)
def release_news():
    user_id = session.get("user_id")
    user = User.query.get(user_id)
    news_type = NewsCategory.query.all()
    cur_news_id = request.args.get('news_id')
    cur_news = News.query.get(cur_news_id) if cur_news_id else None
    # print(cur_news.category_id)
    if request.method == 'GET':
        return render_template('news/user_news_release.html', user=user, category_list=news_type, news=cur_news)
    elif request.method=='POST':
        params1 = request.form
        headline = params1.get('headline')
        type_id = params1.get('category')
        summary = params1.get('summary')
        news_pic = request.files.get('news_pic')
        content = params1.get('content')
        pic_name = None
        if cur_news_id:
            if not all([headline, type_id, summary, content]):
                message = "提示信息：数据不完整！"
                return render_template('news/user_news_release.html',
                                       category_list=news_type,
                                       message=message,
                                       news=None)
        else:
            if not all([headline, type_id, summary, content, news_pic]):
                message = "提示信息：数据不完整！"
                return render_template('news/user_news_release.html',
                                       category_list=news_type,
                                       message=message,
                                       news=None)
        if news_pic:
            pic_name = upload_pic_by_qiniu(news_pic)
            print("+++++++++++++++++++++", pic_name)

        if not cur_news:
            cur_news = News()

        cur_news.title = headline
        cur_news.summary = summary
        cur_news.category_id = int(type_id)
        cur_news.content = content
        if news_pic:
            cur_news.pic = pic_name
        cur_news.status = 2
        cur_news.user_id = int(user_id)

        db.session.add(cur_news)
        db.session.commit()

        return redirect('/user/news_list')
    else:
        return render_template('news/user_news_release.html',
                               news=None,
                                       category_list=news_type,
                                       message="请求方法不被允许！")






