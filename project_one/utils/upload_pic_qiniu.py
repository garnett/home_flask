# import qiniu.config
from qiniu import Auth, put_data, put_file
from configs import DevelopConfig


def upload_pic_by_qiniu(pic_file, cate=None):
    # 需要填写你的 Access Key 和 Secret Key
    access_key = DevelopConfig.QINIU_AK
    secret_key = DevelopConfig.QINIU_SK
    # 构建鉴权对象
    q = Auth(access_key, secret_key)
    # 要上传的空间
    bucket_name = DevelopConfig.QINIU_SPACE
    # 上传后保存的文件名
    key = 'my-p1-logo.png'
    # 生成上传 Token，可以指定过期时间等
    token = q.upload_token(bucket_name)
    # 要上传文件的本地路径
    # localfile = './static/news/images/cat.jpg'
    if not cate:
        ret, info = put_data(token, None, pic_file.read())
    else:
        ret, info = put_file(token, None, pic_file)
    print(info)
    print(ret)
    print(ret['key'])
    pic_name = ret['key']

    return pic_name