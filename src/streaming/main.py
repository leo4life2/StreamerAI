import sqlite3
import atexit
import logging
import subprocess
import time
import os
import uuid
import signal
import pyttsx3
import argparse
from .database import initialize_table, query_comments, mark_comments_as_read
from .settings import DATBASE_PATH, QUESTION_ANSWERING_SCRIPT_PLACEHOLDER
from ..gpt.chains import Chains
from ..gpt.scripts import script_for_product_index

"""
TODOs:
- can we get username for comments?
- can we add timestamp for comments?
- consider looping through all products instead of just picking 1
"""

# parse arguments
parser = argparse.ArgumentParser()
parser.add_argument('--product_index', type=int, required=True, help='')
parser.add_argument('--room_id', type=str, required=True, help='')
parser.add_argument('--live', action='store_true', help='')
args = parser.parse_args()

# array of subprocesses created by this main script, and a cleanup handler
subprocesses = []
def terminate_subprocesses():
    logging.info("atexit invoked terminate_subprocesses, terminating: {}".format(subprocesses))
    for subprocess in subprocesses:
        subprocess.terminate()
atexit.register(terminate_subprocesses)

# insert schema for table if it doesn't exist
connection = sqlite3.connect(DATBASE_PATH)
initialize_table(connection)

# start polling for new comments
if args.live:
    streamchat_filename = os.path.join(os.path.dirname(__file__), "streamchat.py")
    comments_command = command = ['python', streamchat_filename, args.room_id]
    process = subprocess.Popen(comments_command, stdout=subprocess.PIPE)
    subprocesses.append(process)

# grab script based on product index
# TODO: we can loop through all products or make some interesting transition
script = script_for_product_index(args.product_index)
logging.info("loaded script: {}".format(script))

# initialize TTS engine - eventually we should use a different one
engine = pyttsx3.init()
engine.setProperty("voice", "com.apple.speech.synthesis.voice.mei-jia")

# start main runloop
while True:
    for paragraph in script:
        logging.info("processing script paragraph: {}".format(paragraph))
        if paragraph == QUESTION_ANSWERING_SCRIPT_PLACEHOLDER:
            # consider answering comments here
            comment_results = query_comments(connection, args.room_id)
            logging.info("query for comments: {}".format(comment_results))

            read_comments = []
            for comment in comment_results:
                id = comment[0]
                username = comment[1]
                text = comment[2]

                logging.info(f"processing comment: {text}")

                # always grab new chain, prev_context should always be '' here
                chain, prev_context = Chains.get_chain_prevcontext(str(uuid.uuid4()))

                # grab relevant product context
                product_context, ix = Chains.get_idsg_context('', text, '')
                logging.info(f"using product context:\n{product_context}")

                other_products = Chains.get_product_list_text(text)
                other_products_printable = other_products.replace(', ', ',\n')
                logging.info(f"using other products:\n{other_products}")

                response = chain.predict(
                    human_input=text,
                    product_context=product_context,
                    other_available_products=other_products
                )
                logging.info(
                    f"Chat Details:\n"
                    f"Message: {text}\n"
                    f"Response: {response}\n"
                )

                engine.say(response)
                engine.runAndWait()

                read_comments.append(id)

            mark_comments_as_read(connection, read_comments)
            logging.info("marked comment ids as read: {}".format(read_comments))
            
        else:
            engine.say(paragraph)
            engine.runAndWait()

    logging.info("finished script, restarting from beginning...")
    time.sleep(1)