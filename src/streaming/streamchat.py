import sqlite3
import schedule
import time
import logging
import argparse
from database import add_comment, get_stream_cursor, save_stream_cursor
from settings import DATBASE_PATH
from fetch_danmu import fetch_comments

parser = argparse.ArgumentParser()
parser.add_argument('room_id', type=str, help='')
args = parser.parse_args()

room_id = args.room_id

def poll_latest_comments():
    try:
        logging.info("Running poll_latest_comments")
        connection = sqlite3.connect(DATBASE_PATH)

        past_cursor = get_stream_cursor(connection, room_id)
        logging.info("fetching existing stream cursor for room_id: {}, existing cursor: {}".format(room_id, past_cursor))

        messages, cursor = fetch_comments(room_id, past_cursor)
        logging.info("got new comments for room_id: {}, messages count: {}, cursor: {}".format(room_id, len(messages), cursor))    

        for message in messages:
            if is_question(message):
                logging.info("saving new message that is a question: {}")
                logging.info("got new comments for room_id: {}, messages: {}, cursor: {}".format(room_id, messages, cursor))
                add_comment(connection, room_id, "test_username", message)
            else:
                continue

        save_stream_cursor(connection, room_id, str(cursor))
        logging.info("saving new stream cursor for room_id: {}, new cursor: {}".format(room_id, cursor))
    except Exception as e:
        logging.exception("poll_latest_comments ran into Exception")

schedule.every(5).seconds.do(poll_latest_comments)

while True:
    schedule.run_pending()
    time.sleep(1)
