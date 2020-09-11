import json

from ronglian_sms_sdk import SmsSDK

accId = '8aaf0708635e4ce00163882d25fe192b'
accToken = 'b875bc6df2494477a62205527c5c72b9'
appId = '8aaf0708635e4ce00163882d26531932'

def send_message(phone, content):
    sdk = SmsSDK(accId, accToken, appId)
    # tid = '容联云通讯平台创建的模板'
    tid = '1'
    mobile = phone
    datas = (content, 5)
    resp = sdk.sendMessage(tid, mobile, datas)
    # print('========================================')
    # print(resp)
    ret = json.loads(resp).get('statusCode')
    return ret

# print(int('000000'))
# print(int('104908'))
