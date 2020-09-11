from flask import Blueprint, render_template, request, jsonify, session, redirect, abort
from models import *
from utils.decorations import login_required

app_news = Blueprint('app_news', __name__)


@app_news.route('/comment/list/<int:news_id>')
def news_comments(news_id):
    is_liked = 0
    ret = {"comments": []}
    user = None
    user_id = session.get("user_id")
    if user_id:
        user = User.query.get(user_id)
    news_obj = News.query.get(news_id)
    if not news_obj:
        abort(404)

    # news_comment_list = news_obj.comments
    news_comment_list = NewsComment.query.filter(
        NewsComment.news_id==news_id, NewsComment.comment_id==None).order_by(
        NewsComment.like_count.desc())
    for comment in news_comment_list:
        is_liked = 0
        if comment in user.like_comments:
            is_liked = 1
        cur_dict = {
            "id": comment.id,
            "msg": comment.msg,
            "avatar": comment.user.avatar_url,
            "nick": comment.user.nick_name,
            "sub_time": comment.update_time.strftime('%Y-%m-%d %H:%M:%S'),
            "like_num": comment.like_count,
            "is_liked": is_liked,
            "cback": []
        }
        for cback in comment.comments:
            # cur_dict["cback"] = []
            cur_dict['cback'].append({
                "cback_user": cback.user.nick_name,
                "cback_msg": cback.msg
            })
        ret["comments"].append(cur_dict)

    return jsonify(ret=ret)


@app_news.route('/')
def index():
    # b875bc6df2494477a62205527c5c72b9
    user_cur = None
    if "user_id" in session:
        user_cur = User.query.get(session["user_id"])
    news_list = News.query.order_by(News.click_count.desc())[0:6]
    # news_list_page = news_list.paginate(cur_page, 4, False)
    return render_template('news/index.html',
                           user=user_cur,
                           web_name="首页-新经咨询",
                           # category_list=type_list,
                           news_list=news_list,
                           )


@app_news.route('/news_list')
def get_news_data():
    has_data = 1
    select_type = int(request.args.get("category_id"))
    cur_page = int(request.args.get("page", 1))
    news_data = News.query
    if not select_type == 0:
        news_data = news_data.filter_by(category_id=select_type)
    news_list = news_data.order_by( News.click_count.desc(), News.update_time.desc()).paginate(cur_page, 4, False)
    ret = []
    for news in news_list.items:
        news_dic = {
            "pic_url": news.pic_url,
            "id": news.id,
            "title": news.title,
            "content": news.content[0:100],
            "author": news.user.nick_name,
            "author_avatar": news.user.avatar_url,
            "nick_name": news.user.nick_name,
            "update_time": news.update_time.strftime('%Y-%m-%d %H:%M:%S'),
            "author_id": news.user.id
        }
        ret.append(news_dic)
    if not ret:
        has_data = 0
    return jsonify({
        "ret": ret,
        "has_data": has_data,
        "cur_type": select_type,
        "page": cur_page
    })


@app_news.route('/category')
def get_category():
    type_list = NewsCategory.query.all()

    category_list = []
    for cate in type_list:
        category_dic = {}
        category_dic["id"] = cate.id
        category_dic["name"] = cate.name
        category_dic["cur_cate"] = 'cur_cate' + str(cate.id)
        category_list.append(category_dic)
    return jsonify(category_list)


@app_news.route('/detail/<news_id>')
def news_detail(news_id):
    is_my_collect = 0
    is_my_focus = 0
    user=None
    user_id = session.get("user_id")
    if user_id:
        user = User.query.get(user_id)
    news_list = News.query.order_by(News.click_count.desc())[0:6]
    news_info = News.query.get(int(news_id))
    if not news_info:
        abort(404)
    if news_info in user.news_collect:
        is_my_collect = 1
    if news_info.user in user.follow_user:
        is_my_focus=1
    news_comment_list = news_comments(news_id)
    news_info.click_count += 1
    db.session.commit()
    return render_template(
        'news/detail.html',
        web_name="新经咨询-文章详情",
        is_my_collect=is_my_collect,
        news=news_info, user=user,
        news_list=news_list, is_my_focus=is_my_focus,
        news_comment_list=news_comment_list
    )


@app_news.route('/news/collect/<news_id>', methods=['POST'])
# @login_required
def news_collect(news_id):
    action = request.form.get('action')
    user = None
    user_id = session.get("user_id")
    if user_id:
        user = User.query.get(user_id)
    if not user:
        return jsonify(result=1, message="请先登录！")
    news_info = News.query.get(int(news_id))
    if not news_info:
        abort(404)
    if news_info.user.id == user_id:
        return jsonify(result=2, message="这是您自己发布的新闻!")
    if int(action):
        if news_info in user.news_collect:
            return jsonify(result=4, message="您已经收藏该新闻！")
        user.news_collect.append(news_info)
        db.session.commit()
        return jsonify(result=3, message="收藏新闻成功！")
    else:
        if news_info not in user.news_collect:
            return jsonify(result=4, message="您未收藏该新闻！")
        user.news_collect.remove(news_info)
        db.session.commit()
        return jsonify(result=3, message="取消收藏成功！")


@app_news.route('/attention/<attent_user_id>', methods=["POST"])
def attend_user(attent_user_id):
    user = None
    user_id = session.get("user_id")
    if user_id:
        user = User.query.get(user_id)
    if not user:
        return jsonify(result=1, message="请先登录！")
    attend_user_obj = User.query.get(int(attent_user_id))
    if not attend_user_obj:
        abort(404)
    if attend_user_obj in user.follow_user:
        return jsonify(result=3, message="您已经关注了该用户！")
    user.follow_user.append(attend_user_obj)
    attend_user_obj.follow_count += 1
    db.session.commit()
    return jsonify(result=2, message="关注用户成功！", attend_num=attend_user_obj.follow_count)


@app_news.route('/attention/cancel/<cancel_user_id>', methods=["POST"])
def cancel_attend_user(cancel_user_id):
    user = None
    user_id = session.get("user_id")
    if user_id:
        user = User.query.get(user_id)
    if not user:
        return jsonify(result=1, message="请先登录！")
    cancel_user = User.query.get(cancel_user_id)
    if not cancel_user:
        abort(404)
    if cancel_user not in user.follow_user:
        return jsonify(result=2, message="您未关注过该用户！")
    user.follow_user.remove(cancel_user)
    cancel_user.follow_count -= 1
    db.session.commit()
    return jsonify(result=3, message="取消关注成功！", attend_num=cancel_user.follow_count)


@app_news.route('/comment/publish/<int:news_id>', methods=["POST"])
def comment_publish(news_id):
    comment_content = request.form.get('msg')
    if not comment_content:
        return jsonify(result=2, message="评论内容不能为空！")
    user = None
    user_id = session.get("user_id")
    if user_id:
        user = User.query.get(user_id)
    if not user:
        return jsonify(result=1, message="请先登录！")

    news_obj = News.query.get(news_id)
    if not news_obj:
        abort(404)
    comment_obj = NewsComment()
    comment_obj.news_id = news_id
    comment_obj.user_id = user_id
    comment_obj.msg = comment_content
    news_obj.comment_count += 1
    db.session.add(comment_obj)
    db.session.commit()
    return jsonify(result=3, message="评论成功！", comment_num=news_obj.comment_count)


@app_news.route('/like/<int:comment_id>', methods=["POST"])
def like_comment(comment_id):

    action = request.form.get("action")
    user = None
    user_id = session.get("user_id")
    if user_id:
        user = User.query.get(user_id)
    if not user:
        return jsonify(result=1, message="请先登录！")
    comment_obj = NewsComment.query.get(comment_id)
    if not comment_obj:
        abort(404)

    if not action:
        return jsonify(result=2, message="请求错误！请求参数不完整！")

    if int(action) == 0:
        if comment_obj in user.like_comments:
            return jsonify(result=3, message="不能重复操作！")
        user.like_comments.append(comment_obj)
        comment_obj.like_count += 1
        db.session.commit()
    else:
        if comment_obj not in user.like_comments:
            return jsonify(result=3, message="不能重复操作！")
        user.like_comments.remove(comment_obj)
        comment_obj.like_count -= 1
        db.session.commit()

    return jsonify(result=4, message="操作成功！")


@app_news.route('/comment/reply/<int:comment_id>', methods=['POST'])
def comment_reply(comment_id):
    user = None
    user_id = session.get("user_id")
    if user_id:
        user = User.query.get(user_id)
    if not user:
        return jsonify(result=1, message="请先登录！")

    msg = request.form.get('msg')
    news_id = request.form.get('news_id')
    if not all([msg, news_id]):
        return jsonify(result=2, message='请求参数不完整！')
    comment_sub = NewsComment.query.get(comment_id)
    if not comment_sub:
        abort(404)
    if comment_sub in user.comments:
        return jsonify(result=4, message="这是您自己的评论！")

    reply_obj = NewsComment()
    reply_obj.msg = msg
    reply_obj.news_id = news_id
    reply_obj.user_id = user_id
    reply_obj.comment_id = comment_id
    db.session.add(reply_obj)
    db.session.commit()
    return jsonify(result=3, message="回复成功！")





