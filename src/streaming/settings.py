import logging
import os

# configure logging
logging.basicConfig(level=logging.INFO)

DATBASE_PATH = "test.db"

QUESTION_ANSWERING_SCRIPT_PLACEHOLDER = "{question}"

# TTS API
TTS_ACCESS_TOKEN = os.environ.get("TTS_ACCESS_TOKEN")