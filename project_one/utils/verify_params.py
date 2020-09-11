import re


def verify_phone_number(phone):
    pattern = re.compile(r'^1[3-57-9]\d{9}$')
    if re.match(pattern, phone):
        return True
    else:
        return False


def verify_pwd(pwd):
    pattern = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)\w{8,16}$')
    ret = re.match(pattern, pwd)
    if ret:
        return True
    else:
        return False


def verify_email(email):
    pattern = re.compile(r'[\da-zA-Z.]+@[\da-zA-Z]+.(com|cn|net)')
    if re.match(pattern, email):
        return True
    else:
        return False

# verify_pwd('ewesd2')
# print(re.search(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)\w{8,16}$', 'asQ1da7575_'))
# print(re.match(r'[\da-zA-Z.]+@[\da-zA-Z]+.(com|cn|net)', 'qinghuifang.good@huawei.com'))
