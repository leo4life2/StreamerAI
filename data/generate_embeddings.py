import logging
import sys
import os

from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.text_splitter import CharacterTextSplitter
from langchain import OpenAI, VectorDBQA

# KeyError if OPENAPI_API_KEY not set
os.environ["OPENAI_API_KEY"]

# Get all .txt in current directory
filenames = []
for file in os.listdir():
    if file.endswith(".txt"):
        filenames.append(file)

# Read in all .txt from file
texts = []
metadatas = []
for file in filenames:
    file_handle = open(file, 'r')
    data = file_handle.read()
    texts.append(data)
    metadatas.append({'test': 'test'})

# Create vector store from embeddings
embeddings = OpenAIEmbeddings()
vectorstore = Chroma.from_texts(
    texts,
    embeddings,
    metadatas,
    persist_directory='../apis/chat/gpt/data/chroma'
)

# persist to the directory specified above
vectorstore.persist()