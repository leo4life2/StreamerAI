from langchain import LLMChain, PromptTemplate
from langchain.llms import OpenAIChat
from langchain.memory import ConversationBufferWindowMemory
from .prompt import PREFIX
from .retrieval import retrieve_with_embedding, retrieve_with_prompt, retrieve_top_product_names_with_embedding

class Chains:
    chatid_to_chain = {}
    
    @classmethod
    def create_chain(cls, temperature=0.0, verbose=False):

        template = PREFIX + """
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
        if retrieval_method == 'prompt_retrieval':
            return retrieve_with_prompt(message)
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