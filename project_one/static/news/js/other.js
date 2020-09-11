// 解析url中的查询字符串
function decodeQuery(){
    var search = decodeURI(document.location.search);
    return search.replace(/(^\?)/, '').split('&').reduce(function(result, item){
        values = item.split('=');
        result[values[0]] = values[1];
        return result;
    }, {});
}

// news_collect
$(function(){
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
            }else {
                alert(dat.message);
            }
        })
    })

})
