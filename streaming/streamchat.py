import sqlite3
import settings
import schedule
import time
import logging
import comments_databse

def poll_latest_comments():
    logging.debug("Running poll_latest_comments")

    # hit server API to poll for latest comments
    # response = requests.get("www.myexampleapi.com")

    # populate sqlite
    connection = sqlite3.connect(settings.DATBASE_PATH)
    comments_databse.add_comment(connection, "test_streamid", "test_username", "test_comment")

schedule.every(5).seconds.do(poll_latest_comments)

while True:
    schedule.run_pending()
    time.sleep(1)
