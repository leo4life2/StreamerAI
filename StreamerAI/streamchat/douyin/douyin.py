import argparse
import gzip
import logging
import sqlite3
import StreamerAI.streamchat.douyin.message_pb2 as message_pb2
from playwright.sync_api import sync_playwright as playwright
from StreamerAI.settings import DATABASE_PATH
from StreamerAI.streamchat.streamChatHandler import StreamChatHandler
from google.protobuf.json_format import MessageToDict

logger = logging.getLogger("StreamerAI.DouyinHandler")

parser = argparse.ArgumentParser(description="Douyin chat handler")
parser.add_argument('--room_id', type=str, required=True, help='ID of the chat room')
args = parser.parse_args()

# Setting up URL and room_id
url = 'https://live.douyin.com/' + args.room_id
room_id = args.room_id
connection = sqlite3.connect(DATABASE_PATH)

# Instantiating StreamChatHandler
streamChatHandler = StreamChatHandler(room_id, "DOUYIN")

def decompress_payload(payload, headersList):
    """
    Decompress payload if its header indicates it's compressed.

    Args:
        payload: Raw payload data.
        headersList: List of headers associated with the payload.
    Returns:
        Decompressed payload if it's compressed, original payload otherwise.
    """
    for t in headersList:
        if t.key == 'compress_type' and t.value == "gzip":
            return gzip.decompress(payload)
    return payload

def process_message(t):
    """
    Process the received message based on its method type.

    Args:
        t: Received message to be processed.
    Returns:
        A dictionary representing the parsed message, and its method type.
    """
    message_map = {
        "WebcastGiftMessage": message_pb2.GiftMessage(),
        "WebcastChatMessage": message_pb2.ChatMessage(),
        "WebcastMemberMessage": message_pb2.MemberMessage(),
        "WebcastSocialMessage": message_pb2.SocialMessage()
    }

    message_ = message_map.get(t.method)

    if message_:
        message_.ParseFromString(t.payload)
        data = MessageToDict(message_, preserving_proto_field_name=True)
        return data, t.method
    else:
        return {}, None

def wss(websocket):
    """
    Attach framereceived event handler if websocket's url matches the pattern.

    Args:
        websocket: Websocket object.
    """
    if 'douyin.com/webcast/im/push/v2/?' in websocket.url:
        websocket.on('framereceived', wss_onmessage)

def wss_onmessage(framereceived):
    """
    Handle frame received event from websocket.

    Args:
        framereceived: Received frame from websocket.
    """
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
        if method == "WebcastGiftMessage":
            message_content = data.get('common', {}).get('describe')
            streamChatHandler.on_gift(username, message_content)
        elif method == "WebcastChatMessage":
            message_content = data.get('content')
            streamChatHandler.on_comment(username, message_content)
        elif method == "WebcastMemberMessage":
            streamChatHandler.on_join(username)
        elif method == "WebcastSocialMessage":
            streamChatHandler.on_follow(username)

def main():
    """
    Main function to start the chat handler.
    """
    with playwright() as pw:
        browser = pw.chromium.launch(headless=False)
        page = browser.new_page()
        page.on("websocket", wss)
        page.goto(url, timeout=0)

        while True:  # keep the browser open
            page.wait_for_timeout(100000000)