function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(function(){
    $(".news_review").submit(function (e) {
        e.preventDefault();
        var csrf_token=$('#csrf_token').val();
        var opt=$('input[name="action"]:checked').val(); 
        var reason = $('#refuse_reason').val();
        var news_id = $('#get_id').val();
        $.post('/admin/news/review/detail/'+news_id, {
            "reason":reason,
            "action":opt,
            "csrf_token":csrf_token
        }, function (dat) {
            if(dat.ret==1){
                alert(dat.message);
            }else {
                location.href='/admin/news/review';
            }
        })

    })
});

// 点击取消，返回上一页
function cancel() {
    history.go(-1)
}