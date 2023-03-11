from langchain.vectorstores import Pinecone
from langchain import PromptTemplate, LLMChain, OpenAI
from .settings import PINECONE_INDEX, PINECONE_TEXT_KEY, OPENAI_EMBEDDINGS
import os

vectorstore = Pinecone(PINECONE_INDEX, OPENAI_EMBEDDINGS.embed_query, PINECONE_TEXT_KEY)

def retrieve_with_embedding(message):
    # retrieve top document
    documents = vectorstore.similarity_search(message, 1)
    if len(documents) > 0:
        return documents[0].page_content
    return ''

def retrieve_with_prompt(message):
    # handwritten human summaries to file
    template = """
    You are an AI-powered sales assistant who is well-versed in the features and benefits of the product you are selling.
    You have a deep understanding of the Chinese language and can communicate with potential customers in a clear and confident manner.
    With your expertise and knowledge, you can provide personalized recommendations and use your best judgement to decide which product to best recommend.
    Your goal is given a list of product descriptions, return the number of the product description that is most related to the customer's question or statement.

    List of product descriptions:

    1) "日本进口花王马桶去污清洁剂，去污去味，高效洁净不留死角"
    2) "大王Elleair抽取式面巾纸，三层柔韧持久，湿水不易皱，无屑抗敏感，适合宝宝肉内肌肤，方便携带"
    3) "安娜美肌牙膏，意大利原装进口，欧洲先锋护理口腔护理品牌，小苏打薄荷香清新口气，慕斯状膏体泡沫绵密。"

    Customer Question: "Which one should be used for my skin?"
    Product: 1

    Customer Question: {question}
    Product:
    """
    prompt = PromptTemplate(template=template, input_variables=["question"])
    llm_chain = LLMChain(prompt=prompt, llm=OpenAI(temperature=0), verbose=True)
    result = llm_chain.predict(question=message)

    # llm results are messy, sometimes it's "Answer2", "2", or "2大王Elleair抽取..."
    # let's take only numbers, then take the first number
    cleaned_result = ''.join(c for c in result if c in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'])[0:]
    print(cleaned_result)

    number_to_filename = {
        "1": "21.txt",
        "2": "22.txt",
        "3": "18.txt"
    }
    if cleaned_result in number_to_filename:
        filename = "./data/" + number_to_filename[cleaned_result]
        f = open(filename, "r")
        return f.read()

    return ''