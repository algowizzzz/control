from langchain_anthropic import ChatAnthropic
# from langchain_core.agents import ToolCallParser # Corrected import for ToolCallParser
from langchain.agents import AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents.format_scratchpad.tools import format_to_tool_messages
from langchain.agents.output_parsers.openai_tools import OpenAIToolsAgentOutputParser # Corrected import
# Output parser might not be needed here if AgentExecutor handles llm_with_tools output directly
# from langchain_core.output_parsers.json import JsonOutputToolsParser 
# from langchain.tools.render import render_text_description_and_args # No longer rendering tools in system message

from tools import TOOLS, MODEL_NAME, TEMPERATURE, MAX_TOKENS # Import LLM config too
import os # Import os

# Explicitly get API key for ChatAnthropic
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
if not ANTHROPIC_API_KEY:
    print("Warning from agent.py: ANTHROPIC_API_KEY not found. LLM calls may fail.")

# Claude LLM instance (using config from tools.py)
llm = ChatAnthropic(
    api_key=ANTHROPIC_API_KEY,
    model=MODEL_NAME, 
    temperature=TEMPERATURE, 
    max_tokens=MAX_TOKENS
)

# Bind tools to LLM. This is the recommended way for tool usage with LangChain.
llm_with_tools = llm.bind_tools(TOOLS)

# System persona - simplified, as tools are bound separately
system_message_content = (
    "You are a conversational AI assistant specialized in reviewing internal bank controls.\n"
    "You have access to a PRC library of 18,000 controls with 18 attributes each and a set of tools to perform your tasks.\n\n"
    "Capabilities:\n"
    "- Filter controls by ID or attributes\n"
    "- Review controls via 5W, Operational Effectiveness, Design Effectiveness (max 10 at once)\n"
    "- Explain your methodologies and introspect your tools\n"
    "- Update prompt templates for analysis types (5W, OE, DE)\n"
    "- Compare, segment, and contrast controls\n\n"
    "Always respond copiously but concisely, maintain a friendly yet professional tone,\n"
    "and ask follow-up questions if clarification is needed.\n"
    "You must use the provided tools for any task that they are designed for."
    # Tool descriptions removed from here, as llm.bind_tools() handles it.
)

# This prompt structure is more aligned with how tool calling agents are built with LCEL
prompt = ChatPromptTemplate.from_messages([
    ("system", system_message_content),
    MessagesPlaceholder(variable_name="chat_history", optional=True),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

# This runnable produces the AIMessage with potential tool calls or final response
tool_calling_runnable = (
    {
        "input": lambda x: x["input"],
        "agent_scratchpad": lambda x: format_to_tool_messages(x["intermediate_steps"]),
        "chat_history": lambda x: x.get("chat_history", [])
    }
    | prompt
    | llm_with_tools
    | OpenAIToolsAgentOutputParser() # Using OpenAIToolsAgentOutputParser
)

# AgentExecutor takes this runnable and the tools
# The runnable (tool_calling_runnable) should output an AIMessage.
# If it contains tool_calls, AgentExecutor executes them.
# If not, AgentExecutor considers it the final answer.
agent_executor = AgentExecutor(
    agent=tool_calling_runnable, 
    tools=TOOLS, 
    verbose=True,
    # Optionally, define how to get the final output from the AIMessage if it's not a tool call.
    # For many standard cases, AgentExecutor handles this if the runnable outputs an AIMessage.
    # If direct output from AIMessage content is needed: output_key="content"
)

# For compatibility with the existing agent.run() calls in sample_run.py
# we can create a wrapper or directly use agent_executor.invoke

class AgentWrapper:
    def __init__(self, executor):
        self.executor = executor
        self.chat_history = [] # Basic chat history management

    def run(self, input_str):
        response = self.executor.invoke({
            "input": input_str,
            "chat_history": self.chat_history 
        })
        
        # Extract the final output string more robustly
        final_output = response.get('output')
        if isinstance(final_output, list) and final_output:
            if isinstance(final_output[0], dict) and 'text' in final_output[0]:
                final_output_str = final_output[0]['text']
            else:
                # Fallback if the structure is unexpected, but still a list
                final_output_str = str(final_output)
        elif isinstance(final_output, str):
            final_output_str = final_output
        else:
            # General fallback if 'output' is not found or is of an unexpected type
            final_output_str = str(response) 

        self.chat_history.append(("human", input_str))
        self.chat_history.append(("ai", final_output_str))
        return final_output_str

agent = AgentWrapper(agent_executor) 