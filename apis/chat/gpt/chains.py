from langchain import LLMChain, PromptTemplate
from langchain.llms import OpenAIChat
from langchain.memory import ConversationBufferWindowMemory
from .prompt import PREFIX
from .retrieval import retrieve_with_embedding, retrieve_top_product_names_with_embedding

class Chains:
    chatid_to_chain = {}
    
    @classmethod
    def create_chain(cls, temperature=0.0, verbose=False):

        template = """
        You are an AI-powered sales assistant who is well-versed in the features and benefits of the product you are selling.
        You have a deep understanding of the Chinese language and can communicate with potential customers in a clear and confident manner.
        Your goal is to help customers understand how the product can solve their problems and meet their needs, and to convince them that it is the best solution available.
        With your expertise and knowledge, you can provide personalized recommendations and address any concerns or objections that customers may have, ultimately closing the deal and generating sales for the company.

        Use the information in "Product Information" to answer a user's question about a specific product. If a user asks about available products, use the information in "Other Available Products".
        If you are given a question unrelated to the product or list of other available products, you should respond saying that you are only capable of answering questions about available products.

        Product Information:
        {product_context}

        Other Available Products:
        {other_available_products}
        
        Chat History:
        {history}

        Human: {human_input}
        Assistant:"""

        prompt = PromptTemplate(
            input_variables=["history", "human_input", "product_context", "other_available_products"], 
            template=template
        )

        chatgpt_chain = LLMChain(
            llm=OpenAIChat(model_name="gpt-3.5-turbo", temperature=temperature), 
            prompt=prompt, 
            verbose=verbose, 
            memory=ConversationBufferWindowMemory(k=3, memory_key="history", input_key="human_input"), # only keep the last 3 interactions
        )
        
        return chatgpt_chain
    
    @staticmethod
    def get_idsg_context(retrieval_method, message):
        if retrieval_method == 'embedding_retrieval':
            return retrieve_with_embedding(message)
        return retrieve_with_embedding(message)
    
    @staticmethod
    def get_product_list_text(message):
        return '\n'.join(retrieve_top_product_names_with_embedding(message))

    @classmethod
    def get_chain(cls, chatid):
        if chatid in cls.chatid_to_chain:
            return cls.chatid_to_chain[chatid]
        chain = cls.create_chain()
        cls.chatid_to_chain[chatid] = chain
        return chain