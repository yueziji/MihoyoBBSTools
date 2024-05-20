import config
import tools
from loghelper import log
from request import http
import time
from requests.exceptions import Timeout

token = ''
max_retries = 5   #最大重试次数
retries = 0

def game_captcha(gt: str, challenge: str):
    response = geetest(gt, challenge, 'https://passport-api.mihoyo.com/account/ma-cn-passport/app/loginByPassword')
    # 失败返回None 成功返回validate
    if response is None:
        return response
    else:
        return response['validate']


def bbs_captcha(gt: str, challenge: str):
    response = geetest(gt, challenge,
                       "https://webstatic.mihoyo.com/bbs/event/signin-ys/index.html?bbs_auth_required=true&act_id"
                       "=e202009291139501&utm_source=bbs&utm_medium=mys&utm_campaign=icon")
    # 失败返回None 成功返回validate
    if response is None:
        return response
    else:
        return response['validate']


def geetest(gt: str, challenge: str, referer: str):
    print(gt)
    print(challenge)
    
    response = http.post('http://api.ttocr.com/api/recognize', data={
        'appkey': token,
        'gt': gt,
        'challenge': challenge,
        'referer': referer,
        'itemid': 37
    }, timeout=6)
    data = response.json()
    print("开始过验证")
    if data['status'] == 1:
        resultid = data['resultid']
        while retries < max_retries:
            try:
                time.sleep(3)
                resdata = http.post('http://api.ttocr.com/api/results', data={
                    'appkey': token,
                    'resultid': resultid
                }, timeout=12)
                jsondata = resdata.json()
                if jsondata['msg'] == "识别成功":
                    print(jsondata['msg'])
                    return jsondata['data']  # 成功返回validate
            except Timeout:
                print("验证请求超时，重试中")
                retries += 1
            
    else:
        log.warning(data['msg'])  # 打码失败输出错误信息
        return None
    
