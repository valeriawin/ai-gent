from langchain.llms import Ollama
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory

class LLMService:
    def __init__(self, model_name="llama3.2"):
        self.llm = Ollama(model=model_name)
        self.memory = ConversationBufferMemory()
        self.conversation = ConversationChain(
            llm=self.llm,
            memory=self.memory,
            verbose=True
        )
        
    def get_response(self, user_input):
        response = self.conversation.predict(input=user_input)
        return response
        
    def reset_memory(self):
        self.memory = ConversationBufferMemory()
        self.conversation = ConversationChain(
            llm=self.llm,
            memory=self.memory,
            verbose=True
        )
