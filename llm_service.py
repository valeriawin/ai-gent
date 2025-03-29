from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory


class InMemoryChatMessageHistory(BaseChatMessageHistory):
    def __init__(self):
        self._messages = []

    def add_message(self, message):
        self._messages.append(message)

    def clear(self):
        self._messages = []

    @property
    def messages(self):
        return self._messages

    @messages.setter
    def messages(self, messages):
        self._messages = messages


class LLMService:
    def __init__(self, model_name="llama3.2"):
        self.llm = OllamaLLM(model=model_name)
        self.chat_history = InMemoryChatMessageHistory()

        # create prompt template with message history
        prompt = ChatPromptTemplate.from_messages([
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}")
        ])

        chain = prompt | self.llm

        self.conversation = RunnableWithMessageHistory(
            chain,
            lambda session_id: self.chat_history,
            input_messages_key="input",
            history_messages_key="chat_history"
        )

    def get_response(self, user_input):
        response = self.conversation.invoke(
            {"input": user_input},
            config={"configurable": {"session_id": "default"}}
        )
        return response

    def reset_memory(self):
        self.chat_history.clear()
