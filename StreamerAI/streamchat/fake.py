import sqlite3
import logging
import uuid
import argparse
import asyncio
import time

from StreamerAI.database.database import Stream, Comment
from StreamerAI.settings import DATABASE_PATH
from StreamerAI.streaming.question_classifier import QuestionDetector
from .base import StreamChatBaseHandler
from StreamerAI.gpt.chains import Chains
from StreamerAI.database.database import StreamCommentsDB, Stream, Comment, Product, Asset

logger = logging.getLogger("[FAKE]StreamerAI.FakeHandler")

parser = argparse.ArgumentParser()
parser.add_argument('--room_id', type=str, help='')
args = parser.parse_args()

room_id = args.room_id

class FakeHandler(StreamChatBaseHandler):
    
    async def on_heartbeat(self, message: str):
        pass

    async def on_comment(self, message: str):
        if not QuestionDetector.is_question(message):
            logger.info("not adding new comment because it's not a question")
            return
        
        stream = Stream.select().where(Stream.identifier == room_id).get()
        past_cursor = stream.cursor
        logger.info("fetching existing stream cursor for room_id: {}, existing cursor: {}".format(room_id, past_cursor))

        username = "屁屁"
        text = message

        response = self.get_comment_response(username, text)
        if not response:
            logger.info("could not generate response, skipping comment")
            return

        new_comment = Comment.create(stream=stream, username="屁屁", comment=message, read=False, reply=response)
        logger.info("adding new comment: {} for room_id: {}".format(new_comment, room_id))

        fake_cursor = str(uuid.uuid4())
        stream.cursor = fake_cursor
        stream.save()
        logger.info("saving new stream cursor for room_id: {}, new cursor: {}".format(room_id, fake_cursor))

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
