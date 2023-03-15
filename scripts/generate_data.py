import logging
import sys
import os

from langchain.vectorstores import Pinecone
from apis.chat.gpt.settings import PINECONE_INDEX, PINECONE_INDEX_NAME, PINECONE_TEXT_KEY, OPENAI_EMBEDDINGS

from openpyxl import load_workbook

def generate_and_load_embeddings():
    # array of texts to ingest
    texts = []

    # load workbook
    workbook = load_workbook(filename = "data/data.xlsx")
    for worksheet in workbook.worksheets:
        # for each worksheet, generate tuples of "label" and actual "value"
        label_value_tuples = []
        for row_num in range(1, 1000):
            label_cell = worksheet["A" + str(row_num)]
            value_cell = worksheet["B" + str(row_num)]
            if label_cell.value == None or value_cell.value == None:
                break
            label_value_tuple = str(label_cell.value) + ": " + str(value_cell.value)
            label_value_tuples.append(label_value_tuple)
            print("Generated new tuple: {}".format(label_value_tuple))

        # join the tuples together w/ newlines to form text
        text = "\n".join(label_value_tuples)
        texts.append(text)
        print("Appended new text: {}".format(text))

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

def generate_and_write_text_files():
    # load workbook
    workbook = load_workbook(filename = "data/data.xlsx")
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
            print("Generated new tuple: {}".format(label_value_tuple))

        file_name = str(index + 1) + ".txt"

        # join the tuples together w/ newlines to form text
        text = "\n".join(label_value_tuples)

        # write to file
        file_name = "data/" + str(index + 1) + ".txt"
        f = open(file_name, "w")
        f.write(text)
        print("Wrote to file: {} text: {}".format(file_name, text))