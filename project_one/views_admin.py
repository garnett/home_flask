from datetime import datetime

from flask import Blueprint, render_template, request, jsonify, session, current_app, abort

from utils.decorations import LoginRequire
from utils.verify_params import verify_pwd, verify_phone_number
from utils.upload_pic_qiniu import upload_pic_by_qiniu
from utils.pic_upload_help import *
from models import *
from configs import logger_console, logger_file

app_admin = Blueprint('app_admin', __name__)


@app_admin.route('/login', methods=['GET', 'POST'])
def login_admin():
    if request.method=='GET':
        return render_template('admin/login.html', msg=1)
    elif request.method == 'POST':
        name = request.form.get('username')
        pwd = request.form.get('password')
        if not all([name, pwd]):
            return render_template('admin/login.html', msg="错误提示: 请输入用户名和密码！")
        if not verify_pwd(pwd):
            render_template('admin/login.html', msg="错误提示: 用户名或密码错误！")

        admin_user = User.query.filter(User.is_admin == 1, User.nick_name == name).first()
        if not admin_user:
            return render_template('admin/login.html', msg="错误提示: 用户名或密码错误！")
        if not admin_user.check_pwd(pwd):
            return render_template('admin/login.html', msg="错误提示: 用户名或密码错误！")
        session['admin_id'] = admin_user.id
        print(admin_user.avatar_url)
        return render_template('admin/index.html', user=admin_user, msg=1)


@app_admin.route('/logout')
@LoginRequire(is_admin=1)
def logout_admin():
    session.pop('admin_id')
    return render_template('admin/login.html')


@app_admin.route('/')
@LoginRequire(is_admin=1)
def index_admin():
    admin_user_id = int(session["admin_id"])
    user = User.query.get(admin_user_id)
    return render_template('admin/index.html', user=user)


@app_admin.route('/user/count')
@LoginRequire(is_admin=1)
def user_count():
    total_user_num = User.query.filter(User.is_admin==False).count()
    now_time = datetime.now()
    redis_key = "login_%d_%02d_%02d" % (now_time.year, now_time.month, now_time.day)
    mouth_num = User.query.filter(
        User.create_time>=datetime(now_time.year, now_time.month, 1
                                   )).count()
    day_num = User.query.filter(
        User.create_time>=datetime(now_time.year, now_time.month, now_time.day
                                   )).count()
    hour_list = current_app.redis_client.hkeys(redis_key)
    hour_list = [h.decode('utf-8') for h in hour_list]
    num_list = []
    for cur in hour_list:
        num = current_app.redis_client.hget(redis_key, cur)
        if not num:
            num = 0
        num_list.append(int(num))

    return render_template(
        'admin/user_count.html',
        total_user_num=total_user_num,
        mouth_num=mouth_num,
        day_num=day_num,
        hour_list=hour_list,
        num_list=num_list
    )


@app_admin.route('/user/list')
@LoginRequire(is_admin=1)
def user_list():
    cur_page = int(request.args.get('page', 1))
    user_obj_page = User.query.order_by(User.follow_count.desc()).filter_by(is_admin=False).paginate(cur_page, 2, False)
    user_obj_list = user_obj_page.items
    total_page = user_obj_page.pages
    return render_template(
        'admin/user_list.html',
        user_li=user_obj_list,
        total_page=total_page,
        page=cur_page
    )


@app_admin.route('/news/review')
@LoginRequire(is_admin=1)
def news_review():
    return render_template('admin/news_review.html')


@app_admin.route('/news/review/detail/<int:news_id>', methods=['GET', 'POST'])
@LoginRequire(is_admin=1)
def news_review_detail(news_id):
    # 0--未通过  1--审核中  2--已通过
    news_obj = News.query.get(news_id)
    if not news_obj:
        abort(404)
    if request.method == 'GET':
        return render_template('admin/news_review_detail.html', news_obj=news_obj)
    elif request.method == 'POST':
        action = request.form.get("action")
        reason = request.form.get('reason', '')
        if (not action) or (action=="reject" and reason==''):
            return jsonify(ret=1, message='请求参数不完整！')
        if action == "accept":
            news_obj.status = 2
            news_obj.reason = ''
        else:
            news_obj.status = 0
            news_obj.reason = reason
        db.session.commit()
        return jsonify(ret=2, message='操作成功！')



@app_admin.route('/news/review/list')
@LoginRequire(is_admin=1)
def get_news_info():
    cur_page = request.args.get("page", 1)
    search_params = request.args.get('params', '')
    news_info = News.query
    if search_params:
        news_info = news_info.filter(News.title.contains(search_params))
    news_info = news_info.order_by(News.id.desc()).paginate(int(cur_page), 3, False)
    news_info_list = news_info.items
    total_page = news_info.pages
    news_list = []
    for news in news_info_list:
        news_dict = {
            "id": news.id,
            "title": news.title,
            "create_time": news.create_time.strftime('%Y-%m-%d %H:%M:%S'),
            "status": news.status
        }
        news_list.append(news_dict)
    return jsonify(news_list=news_list, total_page=total_page)


@app_admin.route('/news/edit')
@LoginRequire(is_admin=1)
def news_edit():
    return render_template('admin/news_edit.html')


@app_admin.route('/news/edit/detail/<int:news_id>', methods=['GET','POST'])
@LoginRequire(is_admin=1)
def news_edit_detail(news_id):
    news_obj = News.query.get(news_id)
    if not news_obj:
        abort(404)
    if request.method == 'GET':
        return render_template('admin/news_edit_detail.html', news_id=news_id)


@app_admin.route('/news/info/<int:news_id>')
@LoginRequire(is_admin=1)
def get_news_detail_info(news_id):
    news_obj = News.query.get(news_id)
    if not news_obj:
        abort(404)
    news_info = {
        "news_title": news_obj.title,
        "news_summary": news_obj.summary,
        "news_pic": news_obj.pic_url,
        "news_content": news_obj.content,
        "news_type": news_obj.category.id,
    }
    return jsonify(news_info=news_info)


@app_admin.route('/news/modify/<int:news_id>', methods=['POST'])
@LoginRequire(is_admin=1)
def modify_news_info(news_id):
    news_obj = News.query.get(news_id)
    if not news_obj:
        abort(404)
    news_title = request.form.get('title', '')
    news_summary = request.form.get('summary', '')
    news_content = request.form.get('content', '')
    news_cate = request.form.get('category', 0)
    # pic_data = request.files.get('pic_data', '')
    pic_data = request.form.get('pic_data', '')
    if not all([news_title, news_summary, news_content, news_cate]):
        return jsonify(ret=1, message='请求参数不完整！')
    if pic_data:
        txt_path, cur_t = write_pic_txt(pic_data)
        pic_file_path = write_pic(pic_data, cur_t, txt_path)
        try:
            ret = upload_pic_by_qiniu(pic_file_path, cate=1)
            # print('++++++++++++++++++++++++++++++++++++++++++++')
            # print(ret)
        except Exception as e:
            logger_console.error("upload picture failed because %s" % str(e))
            logger_file.error("upload picture failed because %s" % str(e))
            return jsonify(ret=2, message="仅支持png,jpeg格式的图片！")
        news_obj.pic = ret
        rm_temp_file([txt_path, pic_file_path])
        logger_file.info("删除临时文件成功！")
    news_obj.title = news_title
    news_obj.summary = news_summary
    news_obj.content = news_content
    news_obj.category_id = int(news_cate)
    db.session.commit()

    return jsonify(ret=3, message="修改成功！")



@app_admin.route('/news/type')
@LoginRequire(is_admin=1)
def news_type():
    return render_template('admin/news_type.html')


@app_admin.route('/add/category', methods=['POST'])
@LoginRequire(is_admin=1)
def add_category():
    name = request.form.get('name', '')
    action = request.form.get('action', '')
    cur_id = int(request.form.get('cate_id', 0))
    if not all([name, action]):
        return jsonify(ret=1, message='请求参数不完整！')

    cate_obj = NewsCategory.query.filter_by(name=name).count()
    if cate_obj:
        return jsonify(ret=2, message="该分类已存在~！")
    if action == 'add':
        cate = NewsCategory()
        cate.name = name
        db.session.add(cate)
        db.session.commit()
    else:
        cur_cate = NewsCategory.query.get(cur_id)
        if not cur_cate:
            abort(404)
        cur_cate.name = name
        db.session.commit()
    return jsonify(ret=3, message="添加成功！")


@app_admin.route('/del/category', methods=['POST'])
@LoginRequire(is_admin=1)
def del_category():
    cur_id = int(request.form.get('cate_id', 0))
    if not cur_id:
        abort(404)
    cur_cate = NewsCategory.query.get(cur_id)
    if not cur_cate:
        abort(404)
    cur_cate.is_delete = True
    db.session.commit()
    return jsonify(ret=1, message="删除成功！")






