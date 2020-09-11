function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}


$(function () {
    $('.pass_info').submit(function (e) {
        e.preventDefault();

        var old = $('#old_pwd').val();
        var new_pass = $('#new_pwd').val();
        var sure_pass = $('#sure_pwd').val();
        var care_info = $('.error_tip');

        $('#old_pwd').prop({value: ''});
        $('#new_pwd').prop({value: ''});
        $('#sure_pwd').prop({value: ''});
        $.post('/user/modify/pwd', {
            'csrf_token':$('#csrf_token').val(),
            'old_pwd':old,
            'new_pwd':new_pass,
            'again':sure_pass
        },function (data) {
            if(data.result==0){
                alert(data.message);
                $('.error_tip').css("display", "block");
                $('.error_tip').text('提示信息：' + data.message);
                return;
            }
            else if(data.result==1){
                alert(data.message);
                $('.login_form_con', parent.document).show();
            }else {
                alert('未知错误，请重试！')
            }
        })

    })
});