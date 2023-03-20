from langchain.vectorstores import Pinecone
from langchain import PromptTemplate, LLMChain, OpenAI
from openpyxl import load_workbook
from apis.chat.gpt import settings
import os

vectorstore = Pinecone(settings.PINECONE_INDEX, settings.OPENAI_EMBEDDINGS.embed_query, settings.PINECONE_TEXT_KEY)

def get_product_description(worksheet):
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
    return text

def get_product_name(worksheet):
    value_cell = worksheet["B1"]
    if value_cell.value == None:
        return ""
    name = str(value_cell.value)
    return name.replace("\n", "")

def get_worksheet_with_index(index):
    workbook = load_workbook(filename = "./apis/chat/gpt/data/data.xlsx")
    return workbook.worksheets[index]

def retrieve_top_product_names_with_embedding(message, k=10):
    documents = vectorstore.similarity_search(message, k)
    if len(documents) == 0:
        return []

    results = []
    for document in documents:
        index = int(document.metadata['index'])
        if index:
            worksheet = get_worksheet_with_index(index)
            name = get_product_name(worksheet)
            results.append(name)

    return results

def retrieve_with_embedding(message):
    # retrieve top document
    print("message {}".format(message))
    documents = vectorstore.similarity_search(message, 1)
    if len(documents) > 0:
        document = documents[0]
        index = int(document.metadata['index'])
        worksheet = get_worksheet_with_index(index)
        desc = get_product_description(worksheet)
        return desc, index
    return '', 0
