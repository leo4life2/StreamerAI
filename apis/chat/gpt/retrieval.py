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

    ```
    1) "德国双心辅酶q10胶囊ql0心脏保健品中老年成人coq10心脑血管30粒"
    2) "Schiff 旭福液体钙片补钙维生素 d3 碳酸钙加镁中老年人钙片 90 粒*2"
    3) "ISDG 日本进口夜间酵素 232 种植物果蔬水果孝素 120 粒/袋*2"
    4) "biowell 羊胎素胶囊内调保养女性羊胚胎羊胎盘提取物进口第四餐"
    5) "NYO3护肝片挪威进口140倍奶蓟草小绿盾水飞蓟素加班熬夜应酬保健"
    6) "NYO3挪威原装进口纯南极磷虾油56%高海洋磷脂鱼油升级omega-3x2瓶"
    7) "Biowell新加坡进口富硒片 活性有机天然酵母硒元素第4代硒片维e"
    8) "美国进口viyouth维养思益生菌成年大人益生菌食品调理养胃"
    9) "MDC小腰精酵素30粒左旋肉碱黑生姜日夜间植物本孝素促进脂肪分解"
    10) "澳乐维他澳洲原装进口虾青素雨生红球藻胶囊口服精华90粒/瓶"
    11) "SpringLeaf绿芙澳洲进口黑蜂胶软胶囊高浓度2000mg365粒"
    12) "俄罗斯蓝胖子羊奶粉"
    13) "ISDG 日本进口甜蜜习惯抗糖丸 热控片非白芸"
    14) "德国大马膏原装正品进口七叶庄园马栗按摩凝胶颈肩腰腿损伤修复油"
    15) "意大利进口小苏打牙膏"
    16) "日本近江兄弟小熊防晒霜防紫外线女夏季清爽学生军训身体防晒乳男"
    17) "日本进口花王马桶去污清洁剂"
    18) "日本大王爱璐儿elleair超软宝宝专用保湿纸巾抽纸婴儿用纸60抽*4"
    ```

    The returned number must be between 1 and 18.

    Customer Question: "Which one should be used for my skin?"
    Product: 1

    Customer Question: {question}
    Product:
    """
    prompt = PromptTemplate(template=template, input_variables=["question"])
    llm_chain = LLMChain(prompt=prompt, llm=OpenAI(temperature=0), verbose=True)
    result = llm_chain.predict(question=message)
    print("llm returned: {}".format(result))

    # llm results are messy, sometimes it's "Answer2", "2", or "2大王Elleair抽取..."
    # let's take only numbers, then take the first number
    cleaned_result = ''.join(c for c in result if c in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'])[0:]
    print("cleaned_result: {}".format(cleaned_result))
    if cleaned_result == None:
        return ''

    filename = "./data/" + str(cleaned_result) + ".txt"
    f = open(filename, "r")
    text = f.read()
    print("returned text: {}".format(text))
    return text