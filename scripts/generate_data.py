import logging
import sys
import os
from openpyxl import load_workbook
from apis.chat.gpt.settings import PINECONE_INDEX, PINECONE_INDEX_NAME, PINECONE_TEXT_KEY, OPENAI_EMBEDDINGS

# import pinecone
# from langchain.embeddings.openai import OpenAIEmbeddings
# from langchain.vectorstores import Pinecone

# PINECONE_API_KEY = os.environ["PINECONE_API_KEY"]
# PINECONE_ENVIRONMENT = "us-east-1-aws"
# PINECONE_INDEX_NAME = "langchain-test4"
# PINECONE_TEXT_KEY = "text"

# OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
# OPENAI_EMBEDDINGS = OpenAIEmbeddings()

# # initialize pinecone
# pinecone.init(
#     api_key=PINECONE_API_KEY,
#     environment=PINECONE_ENVIRONMENT
# )
# PINECONE_INDEX = pinecone.Index(PINECONE_INDEX_NAME)

# array of texts to ingest
texts = []
metadatas = []

# load workbook
workbook = load_workbook(filename = "./apis/chat/gpt/data/data.xlsx")
for index, worksheet in enumerate(workbook.worksheets):
    # for each worksheet, generate tuples of "label" and actual "value"
    label_value_tuples = []
    for row_num in range(1, 1000):
        label_cell = worksheet["A" + str(row_num)]
        value_cell = worksheet["B" + str(row_num)]
        if label_cell.value == None or value_cell.value == None:
            break
        label_value_tuple = str(label_cell.value) + ": " + str(value_cell.value)
        label_value_tuples.append(label_value_tuple)

    # join the tuples together w/ newlines to form text
    text = "\n".join(label_value_tuples)
    texts.append(text)
    print("Appended new text: {}".format(text))
    metadata = {
        "index": index
    }
    metadatas.append(metadata)
    print("Appended new metadata: {}".format(metadata))

print("using index: {}".format(PINECONE_INDEX_NAME))

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
