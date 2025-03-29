from langchain.agents import initialize_agent, AgentType
from langchain_ollama import OllamaLLM
from langchain_core.tools import Tool
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

        def search_tool(query):
            return f"Search results for: {query}"

        tools = [
            Tool(
                name="search",
                func=search_tool,
                description="useful for searching information"
            )
        ]

        self.agent_executor = initialize_agent(
            tools,
            self.llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True
        )

        chat_prompt = ChatPromptTemplate.from_messages([
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}")
        ])

        chain = chat_prompt | self.llm

        self.conversation = RunnableWithMessageHistory(
            chain,
            lambda session_id: self.chat_history,
            input_messages_key="input",
            history_messages_key="chat_history"
        )

    def get_response(self, user_input):
        if any(keyword in user_input.lower() for keyword in ["search", "find", "look up"]):
            return self.agent_executor.invoke({"input": user_input})

        response = self.conversation.invoke(
            {"input": user_input},
            config={"configurable": {"session_id": "default"}}
        )
        return response

    def reset_memory(self):
        self.chat_history.clear()