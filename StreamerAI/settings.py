import logging
import os
import pinecone


# configure logging
logging.basicConfig(level=logging.INFO)

# Database settings
DATABASE_PATH = os.path.join(os.path.dirname(__file__), "data", "test.db")

# Prompt settings
QUESTION_ANSWERING_SCRIPT_PLACEHOLDER = "{question}"
ASSET_DISPLAY_SCRIPT_PLACEHOLDER = "{asset:"

# TTS API settings
TTS_ACCESS_TOKEN = os.environ.get("TTS_ACCESS_TOKEN")

# Product context switch threshold
PRODUCT_CONTEXT_SWITCH_SIMILARITY_THRESHOLD = 0.78

# Pinecone settings
PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY")
PINECONE_ENVIRONMENT = "us-east-1-aws"
PINECONE_INDEX_NAME = "streamerai"
PINECONE_TEXT_KEY = "text"

# Initialize Pinecone
pinecone.init(
    api_key=PINECONE_API_KEY,
    environment=PINECONE_ENVIRONMENT
)
PINECONE_INDEX = pinecone.Index(PINECONE_INDEX_NAME)

# OpenAI settings
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

BOOTSTRAP_DATA_DIRECTORY = os.path.join(os.path.dirname(__file__), "data", "bootstrap_data")

LLM_NAME = "gpt-3.5-turbo" # gpt-4 or gpt-3.5-turbo
LLM_TEMPERATURE = 1.0
