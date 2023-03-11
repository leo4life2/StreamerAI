import logging
import sys
import os

from langchain.vectorstores import Pinecone
from settings import PINECONE_INDEX, PINECONE_INDEX_NAME, PINECONE_TEXT_KEY, OPENAI_EMBEDDINGS

# Get all .txt in current directory
filenames = []
for file in os.listdir("data"):
    if file.endswith(".txt"):
        filenames.append("data/" + file)

# Read in all .txt from file
texts = []
for file in filenames:
    file_handle = open(file, 'r')
    data = file_handle.read()
    texts.append(data)

vectorstore = Pinecone.from_existing_index(
    PINECONE_INDEX_NAME,
    OPENAI_EMBEDDINGS,
    PINECONE_TEXT_KEY
)

if len(texts) > 0:
    vectorstore.add_texts(texts)
    print("initialized pinecone and added texts")
else:
    print("no texts found")