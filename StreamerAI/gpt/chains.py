import logging

from langchain import LLMChain, PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferWindowMemory
from langchain.embeddings.openai import OpenAIEmbeddings
from tenacity import retry, wait_random_exponential, stop_after_attempt

from StreamerAI.settings import PRODUCT_CONTEXT_SWITCH_SIMILARITY_THRESHOLD, PINECONE_INDEX, PINECONE_TEXT_KEY
from StreamerAI.gpt.retrieval import Retrieval


class Chains:
    """A class representing a collection of language model chains used for responding to user queries."""

    chatid_to_chain_prevcontext = {}
    retrieval = Retrieval(PINECONE_INDEX, OpenAIEmbeddings(), PINECONE_TEXT_KEY)
    
    @classmethod
    def create_chain(cls, temperature=0.0, verbose=False):
        """Create and return a new language model chain.

        Args:
            temperature (float): the sampling temperature to use when generating responses
            verbose (bool): whether or not to print debugging information

        Returns:
            LLMChain: the newly created language model chain
        """
        template = """You are an AI-powered sales assistant who is well-versed in the features and benefits of the product you are selling.
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
            llm=ChatOpenAI(model_name="gpt-3.5-turbo", temperature=temperature),
            prompt=prompt,
            verbose=verbose,
            memory=ConversationBufferWindowMemory(k=3, memory_key="history", input_key="human_input"), # only keep the last 3 interactions
        )

        return chatgpt_chain

    @classmethod
    @retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(3))
    def get_idsg_context(cls, retrieval_method, message, prev_context):
        """Retrieve product information based on the user's query.

        Args:
            retrieval_method: not currently used
            message (str): the user's query
            prev_context (str): the previous product context

        Returns:
            str: the product context
            int: the product index
        """
        # Currently only using embedding retrieval no matter what
        descr, ix, score = cls.retrieval.retrieve_with_embedding(message)
        logging.info(f"Score is {score}")
        if prev_context and score < PRODUCT_CONTEXT_SWITCH_SIMILARITY_THRESHOLD:
            logging.info("Using old context")
            return prev_context, ix
        return descr, ix
    
    @classmethod
    def get_product_list_text(cls, message):
        """Retrieve a list of available product names based on the user's query.

        Args:
            message (str): the user's query

        Returns:
            str: a formatted string containing a list of available product names
        """
        return '\n'.join(cls.retrieval.retrieve_top_product_names_with_embedding(message))

    @classmethod
    def get_chain_prevcontext(cls, chatid):
        """Retrieve the language model chain and previous product context for the given chatid.
        If the chain does not exist, it creates a new one.

        Args:
            chatid (string): the chat uuid

        Returns:
            tuple: a tuple containing the language model chain and the previous product context
        """
        if chatid not in cls.chatid_to_chain_prevcontext:
            chain = cls.create_chain()
            cls.chatid_to_chain_prevcontext[chatid] = (chain, '')
            
        return cls.chatid_to_chain_prevcontext[chatid]
