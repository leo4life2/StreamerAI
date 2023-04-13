import sqlite3
import logging
import uuid
import argparse
from database import add_comment, get_stream_cursor, save_stream_cursor
from settings import DATBASE_PATH
from question_classifier import is_question

parser = argparse.ArgumentParser()
parser.add_argument('--room_id', type=str, help='')
args = parser.parse_args()

room_id = args.room_id
connection = sqlite3.connect(DATBASE_PATH)

while True:
    new_comment = input("insert stream comment: ")

    if not is_question(new_comment):
        logging.info("[FAKE] not adding new comment because it's not a question")
        continue

    past_cursor = get_stream_cursor(connection, room_id)
    logging.info("[FAKE] fetching existing stream cursor for room_id: {}, existing cursor: {}".format(room_id, past_cursor))

    add_comment(connection, room_id, "test_username", new_comment)
    logging.info("[FAKE] adding new comment for room_id: {}".format(room_id))

    fake_cursor = str(uuid.uuid4())
    save_stream_cursor(connection, room_id, fake_cursor)
    logging.info("[FAKE] saving new stream cursor for room_id: {}, new cursor: {}".format(room_id, fake_cursor))