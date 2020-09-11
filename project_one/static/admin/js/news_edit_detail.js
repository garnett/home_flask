function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(function(){

    file_real = '';
    // var pic_data = $('#pic').val();
    var news_id = $('#get_id').val();
    var news_edit_vue=new Vue({
        el:'.news_edit',
        delimiters:['[[', ']]'],
        data:{
            news_title:'',
            news_summary:'',
            news_pic:'',
            news_content:'',
            news_type:0,
            categorys:[]
        },
        methods:{
            get_category:function () {
                axios.get('/category').then(function (dat) {
                    news_edit_vue.categorys=dat.data;
                })
            },
            get_info:function () {
                axios.get('/admin/news/info/'+news_id).then(function (dat) {
                    news_edit_vue.news_title=dat.data.news_info.news_title;
                    news_edit_vue.news_summary=dat.data.news_info.news_summary;
                    news_edit_vue.news_pic=dat.data.news_info.news_pic;
                    news_edit_vue.news_content=dat.data.news_info.news_content;
                    news_edit_vue.news_type=dat.data.news_info.news_type;
                })
            },
            submit_modify:function () {
                //var pic_data = $('#pic').val();
                //var pic_data1 = $('#pic')[0].files[0];
                var csrf_token = $('#csrf_token').val();
                var req_obj={
                    'csrf_token':csrf_token,
                    'title':this.news_title,
                    'summary':this.news_summary,
                    'content':this.news_content,
                    'category':this.news_type,
                    'pic_data':file_real
                };
                axios({
                    method: 'post',
                    url: '/admin/news/modify/' + news_id,
                    headers: {
                      'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'
                    },

                    transformRequest: [function(data){
                        data = Qs.stringify(req_obj);
                        return data;
                    }]

                }).then(function (dat) {
                    if(dat.data.ret==1){
                        alert(dat.data.message);
                    }else if(dat.data.ret==2){
                        alert(dat.data.message);
                    }else{
                        location.href='/admin/news/edit';
                    }
                })

            }
        },
        created:function () {

        },
        mounted:function () {
            this.get_category();
            this.get_info();
        }
    });



    //$(".news_edit").submit(function (e) {
     //   e.preventDefault()
    //})
});

// 点击取消，返回上一页
function cancel() {
    history.go(-1)
}

function iget(obj){
//解决C:\fakepath问题
    var oFReader = new FileReader();
    var file =obj.files[0];
    oFReader.readAsDataURL(file);
    oFReader.onloadend = function(oFRevent){
        var src = oFRevent.target.result;
        file_real=src;
        //alert(file_real);
        $('#turn_img').attr('src',src);
    };
//判断图片格式
    var fileName=obj.value;
    var suffixIndex=fileName.lastIndexOf(".");
    var suffix=fileName.substring(suffixIndex+1).toUpperCase();
    if(suffix!="BMP"&&suffix!="JPG"&&suffix!="JPEG"&&suffix!="PNG"&&suffix!="GIF"){
        alert( "请上传图片（格式BMP、JPG、JPEG、PNG、GIF等）!");
    }
}
