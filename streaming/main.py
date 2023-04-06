import sqlite3
import settings
import atexit
import logging
import subprocess
import time
import os
import signal
import pyttsx3
import comments_databse

connection = sqlite3.connect(settings.DATBASE_PATH)
subprocesses = []

# insert schema for table if it doesn't exist
comments_databse.initialize_table(connection)

# spawn subprocess to fetch comments and add to sqlite db
def preexec_fn():
    # this passes on any SIGTERM sent to parent process onto the child subprocess
    def handler(signum, frame):
        os.killpg(os.getpgid(0), signal.SIGTERM)
    signal.signal(signal.SIGTERM, handler)
comments_command = command = ['python', 'comments.py']
process = subprocess.Popen(comments_command, stdout=subprocess.PIPE, preexec_fn=preexec_fn)
subprocesses.append(process)

# register a cleanup function to be run upon process termination
def terminate_subprocesses():
    logging.info("atexit invoked terminate_subprocesses, terminating: {}".format(subprocesses))
    for subprocess in subprocesses:
        subprocess.kill()
atexit.register(terminate_subprocesses)

script = [
    'hello there ooga booga',
    'my name is miguel',
    'lol hello'
]

engine = pyttsx3.init()

while True:
    for paragraph in script:
        # read script in chunks
        engine.say(paragraph)
        engine.runAndWait()

        # after each chunk, consider answering questions

    logging.debug("while True loop iteration finished")
    time.sleep(1)