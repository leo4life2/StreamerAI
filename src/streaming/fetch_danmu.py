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

def _get_danmu_(room_id, user_unique_id, existing_cursor):
    cursor_param = existing_cursor if existing_cursor is not None else ''
    params = {
        'room_id': room_id,
        'user_unique_id': user_unique_id,
        'cursor': cursor_param,
        'internal_ext': '',
        'token': token
    }
    res = requests.post(url=ip_ + 'get_danmu', data=params).text
    res = json.loads(res)

    cursor = res['cursor']
    messages = []

    for message in res['messagelist']:
        if 'content' in message:
            danmu = get_danmu(message['content'])
            if danmu:
                messages.append(danmu)
        if 'messagelist' in message:
            for message_ in message['messagelist']:
                if 'content' in message_:
                    danmu = get_danmu(message_['content'])
                    if danmu:
                        messages.append(danmu)
    
    return (messages, cursor)

def fetch_comments(roomid, existing_cursor):
    url = f'https://live.douyin.com/{roomid}'
    room_detail = _get_roomid_(url)
    if room_detail['state'] == '0':
        print("Room is not streaming")
        return ([], None)
    return _get_danmu_(room_id=room_detail['room_id'], user_unique_id=room_detail['user_unique_id'], existing_cursor=existing_cursor)