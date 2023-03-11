from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain import PromptTemplate, OpenAI, LLMChain

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
    template = """
    You are an AI-powered sales assistant who is well-versed in the features and benefits of the product you are selling.
    You have a deep understanding of the Chinese language and can communicate with potential customers in a clear and confident manner.
    With your expertise and knowledge, you can provide personalized recommendations and use your best judgement to decide which product to best recommend.
    Your goal is given a list of product names and product descriptions, return the name that is most related to the customer's question or statement.

    You should only return a product name from the following list below:

    Product Name # Product Description
    - 19.txt # "近江兄弟淘宝官方旗舰店网址"
    - 21.txt # "花王念朵京东自营旗舰店网址"
    - 22.txt # "大王纸"

    Customer Question: "Which one should be used for my skin?"
    Product: 22.txt

    Customer Question: {question}
    Product:
    """
    prompt = PromptTemplate(template=template, input_variables=["question"])
    llm_chain = LLMChain(prompt=prompt, llm=OpenAI(temperature=0), verbose=True)
    result = llm_chain.predict(question=message)

    # llm likes to insert random spaces in result
    cleaned_result = ''.join(c for c in result if c.isalnum() or c == ".")
    print(cleaned_result)

    valid_filenames = ["19.txt", "21.txt", "22.txt"]
    if cleaned_result in valid_filenames:
        filename = "./data/products/" + cleaned_result
        f = open(filename, "r")
        return f.read()

    return ''