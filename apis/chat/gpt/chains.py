from langchain import LLMChain, PromptTemplate
from langchain.llms import OpenAIChat
from langchain.memory import ConversationBufferWindowMemory
from .prompt import PREFIX, IDSG_CONTEXT
from .retrieval import retrieve_with_embedding, retrieve_with_prompt

class Chains:
    chatid_to_chain = {}
    
    @classmethod
    def create_chain(cls, retrieval_method, message, temperature=0.0, verbose=False):
        product_context = cls.get_idsg_context(retrieval_method, message)
        print("Using Product Context: {}".format(product_context))
        template = PREFIX + product_context[0] + """
        {history}

        Human: {human_input}
        Assistant:"""

        prompt = PromptTemplate(
            input_variables=["history", "human_input"], 
            template=template
        )

        chatgpt_chain = LLMChain(
            llm=OpenAIChat(model_name="gpt-3.5-turbo", temperature=temperature), 
            prompt=prompt, 
            verbose=verbose, 
            memory=ConversationBufferWindowMemory(k=3), # only keep the last 3 interactions
        )
        
        return chatgpt_chain
    
    @staticmethod
    def get_idsg_context(retrieval_method, message):
        if retrieval_method == 'embedding_retrieval':
            return retrieve_with_embedding(message)
        if retrieval_method == 'prompt_retrieval':
            return retrieve_with_prompt(message)
        return retrieve_with_embedding(message)

    @classmethod
    def get_chain(cls, chatid, retrieval_method, message):
        if chatid in cls.chatid_to_chain:
            return cls.chatid_to_chain[chatid]
        chain = cls.create_chain(retrieval_method, message)
        cls.chatid_to_chain[chatid] = chain
        return chain