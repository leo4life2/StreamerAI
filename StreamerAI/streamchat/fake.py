import sqlite3
import logging
import uuid
import argparse
import asyncio

from StreamerAI.database import StreamCommentsDB
from StreamerAI.settings import DATABASE_PATH
from StreamerAI.streaming.question_classifier import QuestionDetector
from .base import StreamChatBaseHandler

parser = argparse.ArgumentParser()
parser.add_argument('--room_id', type=str, help='')
args = parser.parse_args()

room_id = args.room_id
connection = sqlite3.connect(DATABASE_PATH)

class FakeHandler(StreamChatBaseHandler):
    async def on_heartbeat(self, message: str):
        pass

    async def on_comment(self, message: str):
        if not QuestionDetector.is_question(message):
            logging.info("[FAKE] not adding new comment because it's not a question")
            return

        past_cursor = StreamCommentsDB.get_stream_cursor(connection, room_id)
        logging.info("[FAKE] fetching existing stream cursor for room_id: {}, existing cursor: {}".format(room_id, past_cursor))

        StreamCommentsDB.add_comment(connection, room_id, "屁屁", message)
        logging.info("[FAKE] adding new comment for room_id: {}".format(room_id))

        fake_cursor = str(uuid.uuid4())
        StreamCommentsDB.save_stream_cursor(connection, room_id, fake_cursor)
        logging.info("[FAKE] saving new stream cursor for room_id: {}, new cursor: {}".format(room_id, fake_cursor))

    async def on_gift(self, message: str):
        pass

    async def on_purchase(self, message: str):
        pass

async def start():
    fake_handler = FakeHandler()
    while True:
        new_comment = input("insert stream comment: ")
        await fake_handler.on_comment(new_comment)

def main():
    asyncio.run(start())
