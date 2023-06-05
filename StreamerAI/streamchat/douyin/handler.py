import argparse
import gzip
import asyncio
import uuid
from StreamerAI.streaming.question_classifier import QuestionDetector
import message_pb2
import logging
from google.protobuf.json_format import MessageToDict
from playwright.sync_api import sync_playwright as playwright

from StreamerAI.database.database import StreamCommentsDB, Stream, Comment
from StreamerAI.settings import DATABASE_PATH
from StreamerAI.streamchat.base import StreamChatBaseHandler

logger = logging.getLogger("StreamerAI.DouyinHandler")
parser = argparse.ArgumentParser()
parser.add_argument('--room_id', type=str, help='')
args = parser.parse_args()

url = 'https://live.douyin.com/' + args.room_id

room_id = args.room_id

class DouyinHandlerWrapper:
    def __init__(self, page):
        self.page = page
        self.dou_handler = DouyinHandler()
        self.event_loop = asyncio.get_event_loop()  # get the running event loop

    def on_gift(self, data):
        username = data.get('user', {}).get('nickname')
        self.event_loop.create_task(self.dou_handler.on_gift(username + ":" + data.get('common', {}).get('describe')))

    def on_comment(self, data):
        username = data.get('user', {}).get('nickname')
        text = data.get('content')
        self.event_loop.create_task(self.dou_handler.on_comment(username + ":" + text))

    def on_member(self, data):
        username = data.get('user', {}).get('nickname')
        self.event_loop.create_task(self.dou_handler.on_member(username))

    def on_social(self, data):
        username = data.get('user', {}).get('nickname')
        self.event_loop.create_task(self.dou_handler.on_social(username))

class DouyinHandler(StreamChatBaseHandler):
    async def on_gift(self, message: str):
        logger.info(f"[DOU] gift: {message}")

    async def on_comment(self, message: str):
        logger.info(f"[DOU] comment: {message}")
        
        if not QuestionDetector.is_question(message):
            logger.info("not adding new comment because it's not a question")
            return
        
        
        stream = Stream.select().where(Stream.identifier == room_id).get()
        past_cursor = stream.cursor
        logger.info("fetching existing stream cursor for room_id: {}, existing cursor: {}".format(room_id, past_cursor))

        username, text = message.split(":")

        response = self.get_comment_response(username, text)
        if not response:
            logger.info("could not generate response, skipping comment")
            return

        new_comment = Comment.create(stream=stream, username=username, comment=message, read=False, reply=response)
        logger.info("adding new comment: {} for room_id: {}".format(new_comment, room_id))

        fake_cursor = str(uuid.uuid4())
        stream.cursor = fake_cursor
        stream.save()
        logger.info("saving new stream cursor for room_id: {}, new cursor: {}".format(room_id, fake_cursor))
        
    async def on_member(self, message: str):
        logger.info(f"[DOU] member: {message}")

    async def on_social(self, message: str):
        logger.info(f"[DOU] social: {message}")

def process_message(t, dou_handler_wrapper):
    message_ = None
    data = {}
    if t.method == "WebcastGiftMessage":
        message_ = message_pb2.GiftMessage()
        dou_handler_wrapper.on_gift(data)
    elif t.method == "WebcastChatMessage":
        message_ = message_pb2.ChatMessage()
        dou_handler_wrapper.on_comment(data)
    elif t.method == "WebcastMemberMessage":
        message_ = message_pb2.MemberMessage()
        dou_handler_wrapper.on_member(data)
    elif t.method == "WebcastSocialMessage":
        message_ = message_pb2.SocialMessage()
        dou_handler_wrapper.on_social(data)

    if message_:
        message_.ParseFromString(t.payload)
        data = MessageToDict(message_, preserving_proto_field_name=True)

    return data, t.method

def wss(websocket, dou_handler_wrapper):
    if 'douyin.com/webcast/im/push/v2/?' in websocket.url:
        websocket.on('framereceived',lambda framereceived: wss_onmessage(framereceived, dou_handler_wrapper))
        
def decompress_payload(payload, headersList):
    for t in headersList:
        if t.key == 'compress_type' and t.value == "gzip":
            return gzip.decompress(payload)
    return payload

def wss_onmessage(framereceived, dou_handler_wrapper):
    o = message_pb2.PushFrame()
    o.ParseFromString(framereceived)
    payload = decompress_payload(o.palyload, o.headersList)

    r = message_pb2.Response()
    r.ParseFromString(payload)

    for t in r.messages:
        data, method = process_message(t, dou_handler_wrapper)
        if not data:
            continue

with playwright() as pw:
    browser = pw.chromium.launch(headless=False)
    page = browser.new_page()
    dou_handler_wrapper = DouyinHandlerWrapper(page)
    page.on("websocket", lambda websocket: wss(websocket, dou_handler_wrapper))
    page.goto(url, timeout=0)
    page.wait_for_timeout(100000000)
