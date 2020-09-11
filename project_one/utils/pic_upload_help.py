import re
import os
import base64
import shutil

from datetime import datetime

temp_base_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'temp_file')

# print(temp_base_dir)


def get_txt_name():
    cur_t = datetime.now().strftime('%Y_%m_%d_%H_%M_%S_%f')
    cur_name = cur_t + '.txt'
    txt_path = os.path.join(temp_base_dir, cur_name)
    return txt_path, cur_t


def get_pic_name(base_data, cur):
    # cur = datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
    pattern = re.compile(r'(?<=data:image/)\w+(?=;base64)')
    try:
        pic_name = re.search(pattern, base_data).group(0)
    except:
        raise FileNotFoundError('文件流格式不正确！')
    cur_name = cur + '.' + pic_name
    pic_path = os.path.join(temp_base_dir, cur_name)
    return pic_path


def write_pic_txt(base_data):
    data_pic = base_data.split(',')[-1]
    file_path, cur_t = get_txt_name()
    with open(file_path, 'w') as f:
        f.write(data_pic)

    return file_path, cur_t


def write_pic(base_data, cur, txt_path):
    # txt_path, cur = get_txt_name()
    pic_path = get_pic_name(base_data, cur)
    fin = open(txt_path, "r")
    fout = open(pic_path, "wb")
    # data_pic = base_s.split(',')[-1]
    base64.decode(fin, fout)
    fin.close()
    fout.close()
    return pic_path


def rm_temp_file(file_path_list):
    try:
        for file_path in file_path_list:
            os.remove(file_path)
    except:
        raise FileNotFoundError("文件不存在！")


def make_temp_dir(path):
    os.mkdir(path)