var currentCid = 0; // 当前分类 id
var cur_page = 1; // 当前页
var total_page = 1;  // 总页数
var data_querying = true;   // 是否正在向后台获取数据
var cur_type = 0;   // 是否正在向后台获取数据
var is_bottom = true;

let wm = new watcher({
            data:{
                a: 0,
                b: 'hello'
            },
            watch:{
                a(newVal,oldVal){
                    console.log(newVal, oldVal); // 111 0
					if(newVal!=oldVal){
						console.log('the data has changed!!!');
						cur_page=1;
						is_bottom = true;
					}
                }
            }
        });
    //wm.a = 111;
	console.log(cur_page);


$(function () {
    menu_vue = new Vue({
        el:'.menu',
        delimiters: ['[[', ']]'],
        data:{
            category_list:[],
            news_list1:[],
            cur_cate: false
        },
        methods:{
            get_category_data:function () {
                axios.get('/category')
                .then(function (dat) {
                  menu_vue.category_list = dat.data;
                })
                .catch(function (error) {
                  console.log(error);
                });

            },
            get_news_type:function (value, event) {
                data_querying = false;
                if(event) {
                    var crr = event.currentTarget;
                    crr.className = 'active';
                    if (crr.dataset.cid == '1') {
                        crr.previousElementSibling.className = '';
                        crr.nextElementSibling.className = '';
                        crr.nextElementSibling.nextElementSibling.className = '';
                        crr.nextElementSibling.nextElementSibling.nextElementSibling.className = '';
                    } else if (crr.dataset.cid == '2') {
                        crr.previousElementSibling.className = '';
                        crr.previousElementSibling.previousElementSibling.className = '';
                        crr.nextElementSibling.className = '';
                        crr.nextElementSibling.nextElementSibling.className = '';
                    } else if (crr.dataset.cid == '3') {
                        crr.previousElementSibling.className = '';
                        crr.previousElementSibling.previousElementSibling.className = '';
                        crr.previousElementSibling.previousElementSibling.previousElementSibling.className = '';
                        crr.nextElementSibling.className = '';
                    } else {
                        crr.previousElementSibling.className = '';
                        crr.previousElementSibling.previousElementSibling.className = '';
                        crr.previousElementSibling.previousElementSibling.previousElementSibling.className = '';
                        crr.previousElementSibling.previousElementSibling.previousElementSibling.previousElementSibling.className = '';
                    }
                }
               //this.cur_cate1 = true;
               var str_fen = 'fen' + value;
               //var str_cate = 'cur_cate' + value;
               try{
                   var click_cid = this.$refs[str_fen][0].dataset.cid;
                   wm.a = click_cid;
                   currentCid = click_cid;
               }
               catch(err){
                   wm.a = 0;
                }

               //alert(click_cid);
               axios.get('/news_list',{
                   params:
                   {
                       category_id:currentCid,
                       page:cur_page
                   }
               })
                .then(function (dat) {
                  //menu_vue.news_list1 = dat.data.ret;

                   if(cur_page==1){
                       conter_con_vue.news_list = dat.data.ret;
                   }else{
                       conter_con_vue.news_list = conter_con_vue.news_list.concat(dat.data.ret);
                   }
                  data_querying=true;
                  //alert(menu_vue.news_list[0].title);
                  if(dat.data.has_data==0){
                       is_bottom=false;
                  }
                  console.log(dat.data.ret);
                  data_querying=true;
                  cur_page=dat.data.page;
                })
                .catch(function (error) {
                  console.log(error);
                });
           }
        },
        mounted:function () {
            this.get_category_data();
        }
    });
    // menu_vue.get_category_data();
    conter_con_vue = new Vue({
       el:'.list_con',
       delimiters: ['[[', ']]'],
       data:{
           news_list:[]
       },
       methods:{
           get_news_data:function () {
               data_querying=false;
               axios.get('/news_list',{
                   params:
                   {
                       category_id:0,
                       page:cur_page
                   }
               })
                .then(function (dat) {
                  data_querying=true;
                  conter_con_vue.news_list = dat.data.ret;
                  data_querying=true;
                  //cur_type = dat.data.cur_type;
                  console.log(data_querying);
                  console.log(dat.data.ret);

                })
                .catch(function (error) {
                  console.log(error);
                });
               data_querying=true;

           }
       }
    });
    conter_con_vue.get_news_data();

    // 首页分类切换
// $('.menu li').click(function () {
//
//         var clickCid = $(this).attr('data-cid');
//         $('.menu li').each(function () {
//             $(this).removeClass()
//         });
//         $(this).addClass('active');
//         currentCid = clickCid;
//         conter_con_vue.get_news_data();
//
//         // if (clickCid != currentCid) {
//         //     // TODO 去加载新闻数据
//         //     currentCid = clickCid;
//         //     cur_page = 0;
//         //     updateNewsData();
//         // }
//     });

    //页面滚动加载相关
    $(window).scroll(function () {

        // 浏览器窗口高度
        var showHeight = $(window).height();

        // 整个网页的高度
        var pageHeight = $(document).height();

        // 页面可以滚动的距离
        var canScrollHeight = pageHeight - showHeight;

        // 页面滚动了多少,这个是随着页面滚动实时变化的
        var nowScroll = $(document).scrollTop();

        if ((canScrollHeight - nowScroll) < 100 && data_querying && is_bottom) {
            // TODO 判断页数，去更新新闻数据
            cur_page = cur_page + 1;
            menu_vue.get_news_type(wm.a);
        }
    });

});


function updateNewsData() {
    // TODO 更新新闻数据
    }
