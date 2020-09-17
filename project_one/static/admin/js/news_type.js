function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(function(){
    var $pop = $('.pop_con');
    var $cancel = $('.cancel');
    var $confirm = $('.confirm');
    var $error = $('.error_tip');
    var $input = $('.input_txt3');
    var sHandler = 'edit';
    var sId = 0;

    var cate_vue=new Vue({
       el:'.common_table',
       delimiters:['[[', ']]'],
       data:{
           cate_list:[]
       },
       methods:{
         get_cate:function () {
             axios.get('/category').then(function (dat) {
                    cate_vue.cate_list=dat.data;
                })
         },
         add_page:function () {
             sHandler='add';
             $pop.find('h3').html('新增分类');
             $input.val('');
             $pop.show();
         },
         edit_page:function (event) {
             sId = event.currentTarget.parentElement.previousElementSibling.previousElementSibling.textContent;
             sHandler='edit';
             $pop.find('h3').html('修改分类');
             $pop.find('.input_txt3').val(event.currentTarget.parentElement.previousElementSibling.textContent);
             $pop.show();
         },
         action_run:function () {
             var req_obj={
                 "csrf_token":$('#csrf_token').val(),
                 "name":$input.val(),
                 "cate_id":sId,
                 "action":sHandler
             };
             axios({
                 method:'post',
                 url:'/admin/add/category',
                 headers: {
                      'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'
                    },
                 transformRequest: [function(data){
                        data = Qs.stringify(req_obj);
                        return data;
                    }]
             }).then(function (dat) {
                 if(dat.data.ret==3){
                     cate_vue.get_cate();
                     $pop.hide();
                     $error.hide();
                 }else {
                     $error.text(dat.data.message);
                     $error.show();
                 }
             })

         },
         rm_page:function (event) {
             sId = event.currentTarget.parentElement.previousElementSibling.previousElementSibling.textContent;
             var req_obj={
                 "csrf_token":$('#csrf_token').val(),
                 "cate_id":sId
             };
             axios({
                 method:'post',
                 url:'/admin/del/category',
                 headers: {
                      'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'
                    },
                 transformRequest: [function(data){
                        data = Qs.stringify(req_obj);
                        return data;
                    }]
             }).then(function (dat) {
                 if(dat.data.ret==1){
                     cate_vue.get_cate();
                 }else {
                     alert('网络错误！')
                 }
             })
         }
       },
       mounted:function () {
           this.get_cate();
       }
    });


    // $a.click(function(){
    //     sHandler = 'edit';
    //     sId = $(this).parent().siblings().eq(0).html();
    //     $pop.find('h3').html('修改分类');
    //     $pop.find('.input_txt3').val($(this).parent().prev().html());
    //     $pop.show();
    // });
    //
    // $add.click(function(){
    //     sHandler = 'add';
    //     $pop.find('h3').html('新增分类');
    //     $input.val('');
    //     $pop.show();
    // });

    $cancel.click(function(){
        $pop.hide();
        $error.hide();
    });

    $input.click(function(){
        $error.hide();
    });

    $confirm.click(function(){
        cate_vue.action_run();

    })
});