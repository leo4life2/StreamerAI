import sqlite3
import logging
import argparse
import asyncio
import blivedm

from StreamerAI.settings import DATABASE_PATH
from StreamerAI.streamchat.streamChatHandler import StreamChatHandler

# Set up a logger for this module.
logger = logging.getLogger("StreamerAI.BiliHandler")

# Define command-line arguments.
parser = argparse.ArgumentParser(description="Bili chat handler")
parser.add_argument('--room_id', type=str, required=True, help='ID of the chat room')
args = parser.parse_args()

# The ID of the room in the chat service.
room_id = args.room_id
connection = sqlite3.connect(DATABASE_PATH)

# Instantiating StreamChatHandler for handling chat in a room on the Bili platform.
streamChatHandler = StreamChatHandler(room_id, "BILI")

class BiliHandlerWrapper(blivedm.BaseHandler):
    """
    A wrapper around Bili's base handler to intercept events and relay them to StreamChatHandler.
    """
    def __init__(self, client: blivedm.BLiveClient):
        super().__init__()
        self.client = client

    async def _on_heartbeat(self, client: blivedm.BLiveClient, message: blivedm.HeartbeatMessage):
        streamChatHandler.on_heartbeat(message)

    async def _on_danmaku(self, client: blivedm.BLiveClient, message: blivedm.DanmakuMessage):
        streamChatHandler.on_comment(message.uname, message.msg)

    async def _on_gift(self, client: blivedm.BLiveClient, message: blivedm.GiftMessage):
        streamChatHandler.on_gift(message.uname, f"赠送{message.gift_name}x{message.num}")

    async def _on_buy_guard(self, client: blivedm.BLiveClient, message: blivedm.GuardBuyMessage):
        streamChatHandler.on_gift(message.username, f"购买{message.gift_name}")

async def start():
    """
    Asynchronously start the Bili live client and handle its events.
    """
    client = blivedm.BLiveClient(room_id, ssl=True)
    handler = BiliHandlerWrapper(client)
    client.add_handler(handler)

    client.start()
    try:
        # Keep the program running.
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        await client.stop_and_close()

def main():
    """
    The main function that starts the Bili chat handler.
    """
    asyncio.run(start())

if __name__ == "__main__":
    main()
