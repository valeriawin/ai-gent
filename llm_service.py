from langchain.agents import initialize_agent, AgentType
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_community.tools.ddg_search import DuckDuckGoSearchRun
from langchain.tools import tool
from langchain_community.tools.shell.tool import ShellTool


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
        self.llm = OllamaLLM(
            model=model_name,
            temperature=0.2,    # lower temperature for more deliberate responses
            num_ctx=4096,       # larger context window for more comprehensive reasoning
            num_predict=1024,   # allow for longer responses
            repeat_penalty=1.1  # discourage repetitive actions
        )
        self.chat_history = InMemoryChatMessageHistory()
        self.has_searched_times = 0

        @tool
        def limited_search(query: str) -> str:
            """Search the web for information. Can only be used 2 times per query."""
            if self.has_searched_times >= 2:
                return "You have already searched 2 times for this query. Please analyze the data you have."
            self.has_searched_times += 1
            search = DuckDuckGoSearchRun()

            return search.run(query)

        @tool
        def limited_shell(command: str) -> str:
            """Execute shell commands on the local machine.
            Use this tool carefully and only when asked to perform local system operations."""
            shell_tool = ShellTool()

            # safety check for potentially harmful commands
            dangerous_commands = ["rm", "mkfs", "dd", ":(){", "sudo", ">", "shutdown"]
            if any(cmd in command for cmd in dangerous_commands):
                return "For safety reasons, I cannot execute potentially harmful commands like deletion, formatting, or system commands."

            return shell_tool.run(command)

        tools = [limited_search, limited_shell]

        self.agent_executor = initialize_agent(
            tools,
            self.llm,
            agent=AgentType.CHAT_ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=5,
            return_intermediate_steps=True
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
        self.has_searched_times = 0

        if any(keyword in user_input.lower() for keyword in ["search", "find", "look up", "run", "execute", "shell"]):
            agent_result = self.agent_executor.invoke({"input": user_input})

            # if agent stopped due to iteration limit, use the gathered info
            if "Agent stopped due to iteration limit" in str(agent_result):
                search_results = ""
                shell_results = ""
                if "intermediate_steps" in agent_result:
                    for step in agent_result["intermediate_steps"]:
                        if step[0].tool == "limited_search":
                            search_results += step[1] + "\n\n"
                        elif step[0].tool == "limited_shell":
                            shell_results += f"Command: {step[0].tool_input}\nResult: {step[1]}\n\n"

                # now ask the LLM to analyze these results and provide a proper response
                if search_results or shell_results:
                    prompt = f"""Based on the following results for "{user_input}", 
please analyze and write a helpful and short response:

"""
                    if search_results:
                        prompt += f"""Search Results:
{search_results}

"""
                    if shell_results:
                        prompt += f"""Shell Results:
{shell_results}

"""
                    prompt += "Concise response:"
                    return self.llm.invoke(prompt)
                else:
                    return "I tried to search or run commands but couldn't find relevant information. Please try again with a more specific query."

            return agent_result.get("output") or agent_result

        response = self.conversation.invoke(
            {"input": user_input},
            config={"configurable": {"session_id": "default"}}
        )
        if isinstance(response, dict):
            return response.get("output") or response
        else:
            return response

    def reset_memory(self):
        self.chat_history.clear()