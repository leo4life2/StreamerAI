from langchain import LLMChain, PromptTemplate
from langchain.llms import OpenAIChat
from langchain.memory import ConversationBufferWindowMemory
from .prompt import PREFIX, IDSG_CONTEXT

class Chains:
    chatid_to_chain = {}
    
    @staticmethod
    def create_chain(temperature=0.0, verbose=False):
        # TODO: hardcoded with the IDSG product context for now.
        template = PREFIX + IDSG_CONTEXT + """
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
    
    @classmethod
    def get_chain(cls, chatid):
        if chatid in cls.chatid_to_chain:
            return cls.chatid_to_chain[chatid]
        
        chain = cls.create_chain()
        cls.chatid_to_chain[chatid] = chain
        return chain