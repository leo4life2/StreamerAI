import sqlite3
import logging
import uuid
import argparse
import asyncio
import blivedm

from ...database.database import add_comment, get_stream_cursor, save_stream_cursor
from ..settings import DATBASE_PATH
from .base import StreamChatBaseHandler

parser = argparse.ArgumentParser()
parser.add_argument('--room_id', type=str, help='')
args = parser.parse_args()

room_id = args.room_id
connection = sqlite3.connect(DATBASE_PATH)

class BiliHandlerWrapper(blivedm.BaseHandler):
    def __init__(self, client: blivedm.BLiveClient):
        super().__init__()
        self.client = client
        self.bili_handler = BiliHandler()

    async def _on_heartbeat(self, client: blivedm.BLiveClient, message: blivedm.HeartbeatMessage):
        await self.bili_handler.on_heartbeat(message.popularity)

    async def _on_danmaku(self, client: blivedm.BLiveClient, message: blivedm.DanmakuMessage):
        await self.bili_handler.on_comment(message.uname + "：" + message.msg)

    async def _on_gift(self, client: blivedm.BLiveClient, message: blivedm.GiftMessage):
        await self.bili_handler.on_gift(f"{message.uname} 赠送{message.gift_name}x{message.num}")

    async def _on_buy_guard(self, client: blivedm.BLiveClient, message: blivedm.GuardBuyMessage):
        await self.bili_handler.on_purchase(f"{message.username} 购买{message.gift_name}")

class BiliHandler(StreamChatBaseHandler):
    async def on_heartbeat(self, message: str):
        print(f'[{self.client.room_id}] 当前人气值：{message}')

    async def on_comment(self, message: str):
        print(f'[{self.client.room_id}] {message}')
        
        if len(message) < 5:
            logging.info("[BILI] not adding new comment because it's not a question")
            return
        
        past_cursor = get_stream_cursor(connection, room_id)
        logging.info("[BILI] fetching existing stream cursor for room_id: {}, existing cursor: {}".format(room_id, past_cursor))
        
        add_comment(connection, room_id, message.split("：")[0], message.split("：")[1])
        logging.info("[BILI] adding new comment for room_id: {}".format(room_id))
        
        bili_cursor = str(uuid.uuid4())
        save_stream_cursor(connection, room_id, bili_cursor)
        logging.info("[BILI] saving new stream cursor for room_id: {}, new cursor: {}".format(room_id, bili_cursor))

    async def on_gift(self, message: str):
        print(f'[{self.client.room_id}] {message}')

    async def on_purchase(self, message: str):
        print(f'[{self.client.room_id}] {message}')
        
async def main():
    await run_single_client()

async def run_single_client():
    client = blivedm.BLiveClient(room_id, ssl=True)
    handler = BiliHandlerWrapper(client)
    client.add_handler(handler)

    client.start()
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        await client.stop_and_close()

if __name__ == '__main__':
    asyncio.run(main())
