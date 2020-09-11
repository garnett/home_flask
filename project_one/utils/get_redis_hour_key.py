from datetime import datetime

def generate_hour_key():
    now_time = datetime.now()
    redis_key = "login_%d_%02d_%02d" % (now_time.year, now_time.month, now_time.day)

    return redis_key


def generate_every_hour():
    now_time = datetime.now()
    # cur_hour = None
    if 20<now_time.hour<=23 or (now_time.hour==19 and now_time.minute>=15):
        cur_hour = 19
    elif 0<=now_time.hour<=7 or (now_time.hour==8 and now_time.minute<=15):
        cur_hour = 8
    elif (now_time.hour==8 and now_time.minute>15) or (now_time.hour==9 and now_time.minute<=15):
        cur_hour = 9
    elif (now_time.hour==9 and now_time.minute>15) or (now_time.hour==10 and now_time.minute<=15):
        cur_hour = 10
    elif (now_time.hour==10 and now_time.minute>15) or (now_time.hour==11 and now_time.minute<=15):
        cur_hour = 11
    elif (now_time.hour==11 and now_time.minute>15) or (now_time.hour==12 and now_time.minute<=15):
        cur_hour = 12
    elif (now_time.hour==12 and now_time.minute>15) or (now_time.hour==13 and now_time.minute<=15):
        cur_hour = 13
    elif (now_time.hour==13 and now_time.minute>15) or (now_time.hour==14 and now_time.minute<=15):
        cur_hour = 14
    elif (now_time.hour==14 and now_time.minute>15) or (now_time.hour==15 and now_time.minute<=15):
        cur_hour = 15
    elif (now_time.hour==15 and now_time.minute>15) or (now_time.hour==16 and now_time.minute<=15):
        cur_hour = 16
    elif (now_time.hour==16 and now_time.minute>15) or (now_time.hour==17 and now_time.minute<=15):
        cur_hour = 17
    elif (now_time.hour==17 and now_time.minute>15) or (now_time.hour==18 and now_time.minute<=15):
        cur_hour = 18
    else:
        cur_hour = 19

    cur_key = "%02d:15" % cur_hour

    return cur_key


def generate_every_hour_new():
    hour_list = ['08:15', '09:15', '10:15', '11:15', '12:15', '13:15', '14:15', '15:15', '16:15', '17:15', '18:15', '19:15']
    now_time = datetime.now()
    cur_key = None
    for index, cur in enumerate(hour_list):
        if now_time.hour < index+8 or (now_time.hour==index+8 and now_time.minute<=15):
            cur_key = cur
            break
    else:
        cur_key = "19:15"
    return cur_key
