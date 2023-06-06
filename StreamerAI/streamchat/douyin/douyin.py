import argparse
import gzip
import logging
import sqlite3
import uuid
from playwright.sync_api import sync_playwright as playwright
import StreamerAI.streamchat.douyin.message_pb2 as message_pb2
from StreamerAI.database.database import Comment, Stream
from StreamerAI.settings import DATABASE_PATH
from StreamerAI.streamchat.base import StreamChatBaseHandler
from google.protobuf.json_format import MessageToDict

logger = logging.getLogger("StreamerAI.DouyinHandler")

parser = argparse.ArgumentParser()
parser.add_argument('--room_id', type=str, help='')
args = parser.parse_args()

url = 'https://live.douyin.com/' + args.room_id
room_id = args.room_id
connection = sqlite3.connect(DATABASE_PATH)

def comment_handler(username: str, text: str):
    logger.info(f"[DOUYIN] comment: {username}: {text}")
    
    stream = Stream.select().where(Stream.identifier == room_id).get()
    past_cursor = stream.cursor
    logger.info("[DOUYIN] fetching existing stream cursor for room_id: {}, existing cursor: {}".format(room_id, past_cursor))

    response = StreamChatBaseHandler.get_comment_response(username, text)
    if not response:
        logger.info("could not generate response, skipping comment")
        return

    Comment.create(stream=stream, username=username, comment=text, read=False, reply=response)
    logger.info("[DOUYIN] adding new comment for room_id: {}".format(room_id))
    
    cursor = str(uuid.uuid4())
    stream.cursor = cursor
    stream.save()
    logger.info("[DOUYIN] saving new stream cursor for room_id: {}, new cursor: {}".format(room_id, cursor))

def decompress_payload(payload, headersList):
    for t in headersList:
        if t.key == 'compress_type' and t.value == "gzip":
            return gzip.decompress(payload)
    return payload

def process_message(t):
    message_ = None
    data = {}
    if t.method == "WebcastGiftMessage":
        message_ = message_pb2.GiftMessage()
    elif t.method == "WebcastChatMessage":
        message_ = message_pb2.ChatMessage()
    elif t.method == "WebcastMemberMessage":
        message_ = message_pb2.MemberMessage()
    elif t.method == "WebcastSocialMessage":
        message_ = message_pb2.SocialMessage()

    if message_:
        message_.ParseFromString(t.payload)
        data = MessageToDict(message_, preserving_proto_field_name=True)

    return data, t.method

def wss(websocket):
    if 'douyin.com/webcast/im/push/v2/?' in websocket.url:
        websocket.on('framereceived',wss_onmessage)

def wss_onmessage(framereceived):
    o = message_pb2.PushFrame()
    o.ParseFromString(framereceived)
    payload = decompress_payload(o.palyload, o.headersList)

    r = message_pb2.Response()
    r.ParseFromString(payload)

    for t in r.messages:
        data, method = process_message(t)
        if not data:
            continue
        
        username = data.get('user', {}).get('nickname')
        # if method == "WebcastGiftMessage":
        #     message_content = data.get('common', {}).get('describe')
        #     print("Gift:", message_content)
        if method == "WebcastChatMessage":
            message_content = data.get('content')
            comment_handler(username, message_content)
        # if method == "WebcastMemberMessage":
        #     print("User just joined:", username)
        # if method == "WebcastSocialMessage":
        #     print("Username just followed streamer:", username)
        
def main():
    with playwright() as pw:
        browser = pw.chromium.launch(headless=False)
        page = browser.new_page()
        page.on("websocket", wss)
        page.goto(url, timeout=0)
        page.wait_for_timeout(100000000)
