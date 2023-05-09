import logging
import os

from langchain import LLMChain, PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferWindowMemory
from langchain.embeddings.openai import OpenAIEmbeddings
from tenacity import retry, wait_random_exponential, stop_after_attempt
from pathlib import Path

from StreamerAI.settings import PRODUCT_CONTEXT_SWITCH_SIMILARITY_THRESHOLD, PINECONE_INDEX, PINECONE_TEXT_KEY, LLM_NAME
from StreamerAI.gpt.retrieval import Retrieval


class Chains:
    """A class representing a collection of language model chains used for responding to user queries."""

    chatid_to_chain_prevcontext = {}
    retrieval = Retrieval(PINECONE_INDEX, OpenAIEmbeddings(), PINECONE_TEXT_KEY)
    
    @classmethod
    def create_chain(cls, temperature=0.3, verbose=False):
        """Create and return a new language model chain.

        Args:
            temperature (float): the sampling temperature to use when generating responses
            verbose (bool): whether or not to print debugging information

        Returns:
            LLMChain: the newly created language model chain
        """
        cwd = Path.cwd()
        template_file_path = os.path.join(cwd, "data", "prompt_template.txt")
        template = open(template_file_path, "r", encoding='utf-8').read()

        prompt = PromptTemplate(
            input_variables=["history", "human_input", "product_context", "other_available_products", "audience_name"],
            template=template
        )

        chatgpt_chain = LLMChain(
            llm=ChatOpenAI(model_name=LLM_NAME, temperature=temperature),
            prompt=prompt,
            verbose=verbose,
            memory=ConversationBufferWindowMemory(k=3, memory_key="history", input_key="human_input"), # only keep the last 3 interactions
        )

        return chatgpt_chain

    @classmethod
    @retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(3))
    def get_product_context(cls, message, prev_context):
        """Retrieve product information based on the user's query.

        Args:
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
