import os
import pinecone
from langchain.embeddings.openai import OpenAIEmbeddings

PINECONE_API_KEY = os.environ["PINECONE_API_KEY"]
PINECONE_ENVIRONMENT = "us-east-1-aws"
PINECONE_INDEX_NAME = "langchain-test3"
PINECONE_TEXT_KEY = "text"

# initialize pinecone
pinecone.init(
    api_key=PINECONE_API_KEY,
    environment=PINECONE_ENVIRONMENT
)
PINECONE_INDEX = pinecone.Index(PINECONE_INDEX_NAME)

OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
OPENAI_EMBEDDINGS = OpenAIEmbeddings()