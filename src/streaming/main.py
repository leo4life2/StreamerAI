import sqlite3
import atexit
import logging
import subprocess
import time
import os
import uuid
import signal
import argparse
import platform
from .database import initialize_table, query_comments, mark_comments_as_read
from .settings import DATBASE_PATH, QUESTION_ANSWERING_SCRIPT_PLACEHOLDER
from .tts import tts
from ..gpt.chains import Chains
from ..gpt.scripts import fetch_scripts
from ..gpt.retrieval import get_product_description_with_index

"""
TODOs:
- can we get username for comments?
- can we add timestamp for comments?
"""

# parse arguments
parser = argparse.ArgumentParser()
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

scripts = fetch_scripts()
logging.info("testing scripts: {}".format(scripts))

while True:
    # consider answering comments here
    comment_results = query_comments(connection, args.room_id)
    logging.info("query for comments: {}".format(comment_results))

    read_comments = []
    for comment in comment_results:
        id = comment[0]
        username = comment[1]
        text = comment[2]

        logging.info(f"processing comment: {text}")

        chain = Chains.create_chain()

        product_context, ix = Chains.get_idsg_context('retrieve_with_embedding', text, None)
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
        
        # TTS
        time_taken = tts(response)
        logging.info(f"Time taken for TTS: {time_taken} seconds")

        read_comments.append(id)

    mark_comments_as_read(connection, read_comments)
    logging.info("marked comment ids as read: {}".format(read_comments))

    time.sleep(1)

# # start main runloop
# while True:
#     for product_index, paragraphs in enumerate(scripts):
#         for paragraph in paragraphs:
#             logging.info("processing script paragraph: {}".format(paragraph))
#             if paragraph == QUESTION_ANSWERING_SCRIPT_PLACEHOLDER:
#                 # consider answering comments here
#                 comment_results = query_comments(connection, args.room_id)
#                 logging.info("query for comments: {}".format(comment_results))

#                 read_comments = []
#                 for comment in comment_results:
#                     id = comment[0]
#                     username = comment[1]
#                     text = comment[2]

#                     logging.info(f"processing comment: {text}")

#                     chain = Chains.create_chain()

#                     # set "prev_context" to be the current product that the bot is describing
#                     prev_context = get_product_description_with_index(product_index)

#                     # grab product context - we must be sufficiently confident before switching away from "prev_context", aka the current product
#                     product_context, ix = Chains.get_idsg_context('retrieve_with_embedding', text, prev_context)
#                     logging.info(f"using product context:\n{product_context}")

#                     other_products = Chains.get_product_list_text(text)
#                     other_products_printable = other_products.replace(', ', ',\n')
#                     logging.info(f"using other products:\n{other_products}")

#                     response = chain.predict(
#                         human_input=text,
#                         product_context=product_context,
#                         other_available_products=other_products
#                     )
#                     logging.info(
#                         f"Chat Details:\n"
#                         f"Message: {text}\n"
#                         f"Response: {response}\n"
#                     )

#                     engine.say(response)
#                     engine.runAndWait()

#                     read_comments.append(id)

#                 mark_comments_as_read(connection, read_comments)
#                 logging.info("marked comment ids as read: {}".format(read_comments))
#             else:
#                 engine.say(paragraph)
#                 engine.runAndWait()

#     logging.info("finished script, restarting from beginning...")
#     time.sleep(1)