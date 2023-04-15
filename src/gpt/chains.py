from langchain import LLMChain, PromptTemplate
from langchain.llms import OpenAIChat
from langchain.memory import ConversationBufferWindowMemory
from .retrieval import retrieve_with_embedding, retrieve_top_product_names_with_embedding
from .settings import PRODUCT_CONTEXT_SWITCH_SIMILARITY_THRESHOLD
import logging

class Chains:
    chatid_to_chain_prevcontext = {}
    
    @classmethod
    def create_chain(cls, temperature=0.0, verbose=False):

        template = """
        You are an AI-powered sales assistant who is well-versed in the features and benefits of the product you are selling.
        Your goal is to help customers understand how the product can solve their problems and meet their needs, and to convince them that it is the best solution available.
        With your expertise and knowledge, you can provide personalized recommendations and address any concerns or objections that customers may have, ultimately closing the deal and generating sales for the company.

        Use the information in "Product Information" to answer a user's question about a specific product. If a user asks about available products, use the information in "Other Available Products".
        If you are given a question unrelated to health or the product or list of other available products, you should respond saying that you are only capable of answering questions about available products.
        However, you are also a health and nutrition expert, so you can answer questions related to these fields. Try to answer your questions in Chinese as much as possible.
        If you are unsure about what product the user is referring to, or if the product information given doesn't seem to match the user's question, ask the user a follow up question to clarify.

        You must respond to all questions in Chinese, even if the question is in a different language

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
    def get_idsg_context(retrieval_method, message, prev_context):
        # Currently only using embedding retrieval no matter what
        descr, ix, score = retrieve_with_embedding(message)
        logging.info(f"Score is {score}")
        if prev_context and score < PRODUCT_CONTEXT_SWITCH_SIMILARITY_THRESHOLD:
            logging.info("Using old context")
            return prev_context, ix
        return descr, ix
    
    @staticmethod
    def get_product_list_text(message):
        return '\n'.join(retrieve_top_product_names_with_embedding(message))

    @classmethod
    def get_chain_prevcontext(cls, chatid):
        """Returns the chain and previous product context for the given chatid.
        If the chain does not exist, it creates a new one.

        Args:
            chatid (string): the chat uuid

        Returns:
            LLMChain: the chain
            str: the previous product context
        """
        if chatid not in cls.chatid_to_chain_prevcontext:
            chain = cls.create_chain()
            cls.chatid_to_chain_prevcontext[chatid] = (chain, '')
            
        return cls.chatid_to_chain_prevcontext[chatid]
