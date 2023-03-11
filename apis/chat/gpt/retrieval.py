from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma

RETRIEVAL_CHARACTER_LIMIT = 500

embeddings = OpenAIEmbeddings()
vectorstore = Chroma(
    embedding_function=embeddings,
    persist_directory='./data/chroma'
)

def retrieve_with_embedding(message):
    # retrieve top document
    documents = vectorstore.similarity_search(message, 1)
    if len(documents) > 0:
        return documents[0].page_content
    return ''

def retrieve_with_prompt(message):
    # handwritten human summaries to file
    summary_to_file = {
        ''
    }
    return