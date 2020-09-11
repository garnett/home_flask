function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}
//Vue.http.options.emulateJSON = true;
//Vue.http.options.headers = {
 // 'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'
//}//;


$(function(){
    comment_vue = new Vue({
        el:".comment_list_con",
        delimiters: ['[[', ']]'],
        data:{
            comment_list:[],
            like_num:0
        },
        methods: {
            get_comment_list: function () {
                var cur_news_id = $('#get_id').val();
                axios.get('/comment/list/' + cur_news_id)
                    .then(function (dat) {
                        comment_vue.comment_list = dat.data.ret.comments;
                    })
            },
            like_comment: function (comment_id, event) {
                var crr = event.currentTarget;
                var action = 0;
                if (crr.className == "has_comment_up fr") {
                    action = 1;
                }
                var obj_j= {
                        'csrf_token': $('#csrf_token').val(),
                        'action': action
                    };
                axios({
                    method: 'post',
                    url: '/like/' + comment_id,
                    headers: {
                      'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'
                    },

                    transformRequest: [function(data){
                        data = Qs.stringify(obj_j);
                        return data;
                    }]

                }).then(function (dat) {
                    if (dat.data.result == 1) {
                        $('.login_form_con').show();
                        $('.register_form_con').hide();
                    } else if (dat.data.result == 2) {
                        alert(dat.data.message);
                    } else if (dat.data.result == 3) {
                        alert(dat.data.message);
                    } else {
                        if (action == 0) {
                            crr.className = "has_comment_up fr";
                        } else {
                            crr.className = "comment_up fr";
                        }
                        comment_vue.get_comment_list();
                    }
                })

            },
            reply_comment:function (comment_id,event) {
                var cur_news_id = $('#get_id').val();
                // var msg = $('#reply_input').val();
                var msg = event.currentTarget.previousElementSibling.value;
                var req_data = {
                    csrf_token: $('#csrf_token').val(),
                    news_id:cur_news_id,
                    msg:msg
                };
                axios({
                    method: 'post',
                    url: '/comment/reply/' + comment_id,
                    headers: {
                      'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'
                    },

                    transformRequest: [function(data){
                        data = Qs.stringify(req_data);
                        return data;
                    }]

                }).then(function (dat) {
                    if (dat.data.result == 1) {
                        $('.login_form_con').show();
                        $('.register_form_con').hide();
                    }else if(dat.data.result==2){
                        alert(dat.data.message);
                    }else if(dat.data.result==4){
                        alert(dat.data.message);
                        $('.reply_input').val('');
                        $('.reply_form').hide();
                    }else {
                        $('.reply_input').val('');
                        $('.reply_form').hide();
                        comment_vue.get_comment_list();
                    }
                })
            }
        },
        mounted: function () {
                this.get_comment_list();
            }
    });

    // 收藏
    $(".collection").click(function () {
        var cur_news_id = $('#get_id').val();
        $.post('/news/collect/'+cur_news_id,{
            'csrf_token':$('#csrf_token').val(),
            'action':1
        },function (dat) {
            if(dat.result==1){
                $('.login_form_con').show();
		        $('.register_form_con').hide();
            }else if(dat.result==2){
                $('.collect_tip').show();
                $('.collection').hide();
            }else if(dat.result==4){
                alert(dat.message);
            }
            else{
                $(".collected").show();
                $(".collection").hide();
            }
        });
    });

    // 取消收藏
    $(".collected").click(function () {
        var cur_news_id = $('#get_id').val();
        $.post('/news/collect/'+cur_news_id,{
            'csrf_token':$('#csrf_token').val(),
            'action':0
        },function (dat) {
            if(dat.result==1){
                $('.login_form_con').show();
		        $('.register_form_con').hide();
            }else if(dat.result==2){
                $('.collect_tip').show();
                $('.collection').hide();
            }else if(dat.result==4){
                alert(dat.message);
            }
            else{
                $(".collected").hide();
                $(".collection").show();
            }
        });
     
    });
    $(".collect_tip").click(function () {
        $('.collection').show();
        $('.collect_tip').hide();
    });

        // 评论提交
    $(".comment_form").submit(function (e) {
        e.preventDefault();
        var cur_news = $('#get_id').val();
        var msg = $('.comment_input').val();
        $.post('/comment/publish/'+cur_news,{
            'csrf_token':$('#csrf_token').val(),
            'msg':msg
        },function (dat) {
            if(dat.result==1){
                $('.login_form_con').show();
		        $('.register_form_con').hide();
            }else if(dat.result==2){
                alert(dat.message)
            }else{
                $('.comment_input').val('');
                comment_vue.get_comment_list();
                $('#top_num').text(dat.comment_num);
                $('#under_num').text(dat.comment_num+'条评论');
            }
        })

    });

    $('.comment_list_con').delegate('a,input','click',function(){

        var sHandler = $(this).prop('class');

        if(sHandler.indexOf('comment_reply')>=0)
        {
            $(this).next().toggle();
        }

        if(sHandler.indexOf('reply_cancel')>=0)
        {
            $(this).parent().toggle();
        }

        // if(sHandler.indexOf('comment_up')>=0)
        // {
        //     var $this = $(this);
        //     if(sHandler.indexOf('has_comment_up')>=0)
        //     {
        //         // 如果当前该评论已经是点赞状态，再次点击会进行到此代码块内，代表要取消点赞
        //         $this.removeClass('has_comment_up')
        //     }else {
        //         $this.addClass('has_comment_up')
        //     }
        // }

        //if(sHandler.indexOf('reply_sub')>=0)
        //{
        //    alert('回复评论')
        //}
    });

        // 关注当前新闻作者
    $(".focus").click(function () {
        var follow_user_id = $('#follow_id').val();
        $.post('/attention/'+follow_user_id, {
            'csrf_token':$('#csrf_token').val()
        }, function (dat) {
            if(dat.result==1){
                $('.login_form_con').show();
		        $('.register_form_con').hide();
            }else if(dat.result==2){
                $('.focus').hide();
                $('.focused').show();
                $('.follows>b').text(dat.attend_num);
            }else {
                alert(dat.message);
            }
        })
    });

    // 取消关注当前新闻作者
    $(".focused").click(function () {
        var follow_user_id = $('#follow_id').val();
        $.post('/attention/cancel/'+follow_user_id, {
            'csrf_token':$('#csrf_token').val()
        }, function (dat) {
            if(dat.result==1){
                $('.login_form_con').show();
		        $('.register_form_con').hide();
            }else if(dat.result==3){
                $('.focus').show();
                $('.focused').hide();
                $('.follows>b').text(dat.attend_num);
            }else {
                alert(dat.message);
            }
        })
    })
});