import os
import re
import numpy as np

from langchain import hub
from langchain_ollama import OllamaLLM, OllamaEmbeddings
from langchain_core.runnables import RunnableWithMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, SystemMessagePromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.memory import ConversationBufferMemory
from langchain.agents import create_react_agent, AgentExecutor
from langchain_community.tools import DuckDuckGoSearchRun, Tool
from langchain.chains import RetrievalQA
from langchain_community.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma


class LLMService:
    def __init__(self, model_name="llama3.2", docs_dir="documents"):
        self.model_name = model_name
        self.llm = OllamaLLM(model=model_name)
        self.memory = ConversationBufferMemory(memory_key="history", return_messages=True)
        self.docs_dir = docs_dir

        # ensure documents directory exists
        os.makedirs(self.docs_dir, exist_ok=True)

        self.tools = self._initialize_tools()
        self._setup_agent()
        self._setup_conversation_chain()

    def _setup_agent(self):
        prompt = hub.pull("hwchase17/react")
        agent = create_react_agent(self.llm, self.tools, prompt)

        self.agent = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            memory=self.memory,
            handle_parsing_errors=True,
            max_iterations=10,  # prevent infinite loops
            max_execution_time=120,  # in seconds
            early_stopping_method="force"
        )

    def _setup_conversation_chain(self):
        prompt = ChatPromptTemplate.from_messages([
            MessagesPlaceholder(variable_name="history"),
            ("human", "{input}"),
        ])

        chain = prompt | self.llm | StrOutputParser()
        self.conversation = RunnableWithMessageHistory(
            chain,
            lambda session_id: self.memory,
            input_messages_key="input",
            history_messages_key="history",
        )

    def _initialize_tools(self):
        def calculator(expression):
            try:
                # remove any non-math characters
                cleaned_expression = re.sub(r'[^0-9+\-*/().^ ]', '', expression)
                return str(eval(cleaned_expression, {"__builtins__": None}, {"np": np}))
            except Exception as e:
                return f"Error calculating expression: {str(e)}"

        search_tool = DuckDuckGoSearchRun()

        # document qa tool - initialize vector store
        try:
            self.embeddings = OllamaEmbeddings(model=self.model_name)
            if os.path.exists(self.docs_dir) and any(os.scandir(self.docs_dir)):
                self.document_qa = self._setup_document_qa()
                document_tool_available = True
            else:
                document_tool_available = False
        except Exception as e:
            print(f"Error setting up document QA: {str(e)}")
            document_tool_available = False

        tools = [
            Tool(
                name="Calculator",
                func=calculator,
                description="Useful for performing mathematical calculations"
            ),
            Tool(
                name="Search",
                func=search_tool.run,
                description="Useful for searching the internet for information"
            )
        ]

        if document_tool_available:
            tools.append(
                Tool(
                    name="DocumentQA",
                    func=self.document_qa.run,
                    description="Useful for answering questions about uploaded documents"
                )
            )

        return tools

    def _setup_document_qa(self):
        loader = DirectoryLoader(self.docs_dir)
        documents = loader.load()

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        doc_texts = text_splitter.split_documents(documents)

        vector_db = Chroma.from_documents(
            documents=doc_texts,
            embedding=self.embeddings,
            persist_directory="chroma_db"
        )

        retriever = vector_db.as_retriever()
        return RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=retriever,
            verbose=True
        )

    def get_response(self, user_input):
        try:
            try:
                # simple check to see if the model responds
                self.llm.invoke("test")
            except Exception as e:
                print(f"Ollama connection error: {str(e)}")
                return "Error: Cannot connect to Ollama service. Please make sure Ollama is running with 'ollama serve' command."

            try:
                # try using the agent with tools
                response = self.agent.invoke({"input": user_input})
                return response["output"]
            except Exception as e:
                print(f"Agent run error: {str(e)}, falling back to conversation chain")
                # use the conversation chain with a session id
                return self.conversation.invoke(
                    {"input": user_input},
                    {"configurable": {"session_id": "default"}}
                )
        except Exception as e:
            print(f"Conversation error: {str(e)}")
            return f"Error processing your request: {str(e)}"

    def upload_document(self, file_path, file_content):
        file_name = os.path.basename(file_path)
        doc_path = os.path.join(self.docs_dir, file_name)

        with open(doc_path, 'wb') as f:
            f.write(file_content)

        self.document_qa = self._setup_document_qa()

        # update tools list if document tool wasn't already in the list
        tool_names = [tool.name for tool in self.tools]
        if "DocumentQA" not in tool_names:
            self.tools.append(
                Tool(
                    name="DocumentQA",
                    func=self.document_qa.run,
                    description="Useful for answering questions about uploaded documents"
                )
            )

            # recreate the agent with updated tools
            self._setup_agent()

        return f"Document {file_name} uploaded successfully"

    def reset_memory(self):
        self.memory = ConversationBufferMemory(memory_key="history", return_messages=True)

        self._setup_agent()
        self._setup_conversation_chain()
