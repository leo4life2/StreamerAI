import sqlite3
import logging
import uuid
import argparse
import asyncio
import blivedm

from database import add_comment, get_stream_cursor, save_stream_cursor
from settings import DATBASE_PATH
from question_classifier import is_question

parser = argparse.ArgumentParser()
parser.add_argument('--room_id', type=str, help='')
args = parser.parse_args()

room_id = args.room_id
connection = sqlite3.connect(DATBASE_PATH)

async def main():
    await run_single_client()

async def run_single_client():
    """
    演示监听一个直播间
    """
    # 如果SSL验证失败就把ssl设为False，B站真的有过忘续证书的情况
    client = blivedm.BLiveClient(room_id, ssl=True)
    handler = MyHandler()
    client.add_handler(handler)

    client.start()
    try:
        # 持续运行直到收到键盘中断
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        await client.stop_and_close()
        
class MyHandler(blivedm.BaseHandler):
    # # 演示如何添加自定义回调
    # _CMD_CALLBACK_DICT = blivedm.BaseHandler._CMD_CALLBACK_DICT.copy()
    #
    # # 入场消息回调
    # async def __interact_word_callback(self, client: blivedm.BLiveClient, command: dict):
    #     print(f"[{client.room_id}] INTERACT_WORD: self_type={type(self).__name__}, room_id={client.room_id},"
    #           f" uname={command['data']['uname']}")
    # _CMD_CALLBACK_DICT['INTERACT_WORD'] = __interact_word_callback  # noqa

    async def _on_heartbeat(self, client: blivedm.BLiveClient, message: blivedm.HeartbeatMessage):
        print(f'[{client.room_id}] 当前人气值：{message.popularity}')

    async def _on_danmaku(self, client: blivedm.BLiveClient, message: blivedm.DanmakuMessage):
        print(f'[{client.room_id}] {message.uname}：{message.msg}')
        
        if not is_question(message.msg):
            logging.info("[BILI] not adding new comment because it's not a question")
            return
        
        past_cursor = get_stream_cursor(connection, room_id)
        logging.info("[BILI] fetching existing stream cursor for room_id: {}, existing cursor: {}".format(room_id, past_cursor))
        
        add_comment(connection, room_id, message.uname, message.msg)
        logging.info("[BILI] adding new comment for room_id: {}".format(room_id))
        
        bili_cursor = str(uuid.uuid4())
        save_stream_cursor(connection, room_id, bili_cursor)
        logging.info("[BILI] saving new stream cursor for room_id: {}, new cursor: {}".format(room_id, bili_cursor))

    async def _on_gift(self, client: blivedm.BLiveClient, message: blivedm.GiftMessage):
        print(f'[{client.room_id}] {message.uname} 赠送{message.gift_name}x{message.num}'
              f' （{message.coin_type}瓜子x{message.total_coin}）')

    async def _on_buy_guard(self, client: blivedm.BLiveClient, message: blivedm.GuardBuyMessage):
        print(f'[{client.room_id}] {message.username} 购买{message.gift_name}')

    async def _on_super_chat(self, client: blivedm.BLiveClient, message: blivedm.SuperChatMessage):
        print(f'[{client.room_id}] 醒目留言 ¥{message.price} {message.uname}：{message.message}')


if __name__ == '__main__':
    asyncio.run(main())