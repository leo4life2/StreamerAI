import json
import time
import requests
import argparse

# token添加作者微信免费获取
token = '12345678'
#ip_为作者服务器，无需更换
ip_ = 'http://49.235.82.99:8082/'
def _get_roomid_(web_url):
    params = {
        'url': web_url,
        'token': token
    }
    res = requests.post(url=ip_ + 'get_roomid', data=params).text
    res = json.loads(res)
    room_id_ = res
    return room_id_

def get_danmu(danmu):
    if danmu in ['关注或者分享了直播间', '进入直播间'] \
        or danmu.startswith("点赞了") \
        or ':送给主播' in danmu:
            return None
    return danmu

def _get_danmu_(room_id, user_unique_id):
    params = {'room_id': room_id,
            'user_unique_id': user_unique_id,
            'cursor': '',
            'internal_ext': '',
            'token': token
            }
    while True:
        res = requests.post(url=ip_ + 'get_danmu', data=params).text
        res = json.loads(res)
        params['cursor'] = res['cursor']
        params['internal_ext'] = res['fetchInterval']
        for message in res['messagelist']:
            if 'content' in message:
                danmu = get_danmu(message['content'])
                if danmu: print(danmu)
            if 'messagelist' in message:
                for message_ in message['messagelist']:
                    if 'content' in message_:
                        danmu = get_danmu(message_['content'])
                        if danmu: print(danmu)
        time.sleep(1)  # 一定要休息1s


# 替换直播地址即可
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("roomid", help="roomid input to the script")
    args = parser.parse_args()
    roomid = args.roomid
    
    url = f'https://live.douyin.com/{roomid}'
    room_detail = _get_roomid_(url)
    if room_detail['state'] == '0':
        print(room_detail)
    else:
        _get_danmu_(room_id=room_detail['room_id'],
                    user_unique_id=room_detail['user_unique_id'])