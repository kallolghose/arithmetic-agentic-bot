from langchain_core.tools import tool
import streamlit as st
from langgraph.types import Command, interrupt


class AgentWorkflow: 

    def __init__(self, thread_id):
        self.thread_id = thread_id
        self.agent = None
        self.agent_state = "INITIALIZED"

    # addition tool
    @tool    # This identifies the following function as a tool to LangGraph
    # in the following statement the function name, the attributes their types and the output type are defined
    def addition(self, x:int, y:int) -> int : 
        # The following docstring describes what the function can do and is used by the LLM to determine whethere this
        # is the tool to be called, and what are its inputs and outputs
        """
        This addition function adds two numbers and returns their sum. 
        It takes two integers as its inputs and the output is an integer.
        """
        return x + y

    # subtraction tool
    @tool
    def subtraction(self, x:int, y:int) -> int : 
        """
        This subtraction function subtracts a number from another and returns the difference. 
        It takes two integers as its inputs and the output is an integer.
        """
        return x - y
    # multiplication tool
    @tool
    def multiplication(self, x:int, y:int) -> int : 
        """
        This multiplication function multiplies two numbers returns the product. 
        It takes two integers as its inputs and the output is an integer.
        """
        return x * y
    # division tool
    @tool
    def division(self, x:int, y:int) -> int : 
        """
        This division function divides one number by another and returns the quotient. 
        It takes two integers as its inputs and the output is an integer.
        """
        return x / y

    @tool
    def human_assistance(self, query: str):
        """Ask human for input."""
        print("Asking for human assistance...")
        self.agent_state="WAITING_FOR_HUMAN"
        interrupt({"query": query})

    @tool
    def get_weather(self, city: str) -> str:  
        """Get weather for a given city."""
        return f"It's always sunny in {city}!"

    def create_agent(self, model, tools, prompt, checkpointer=None, debug=False):
        from langgraph.prebuilt import create_react_agent
        self.agent_state = "CREATED"
        self.agent = create_react_agent(
        model = model,
        prompt = prompt,
        tools = tools,
        checkpointer=checkpointer,
        debug = debug)
        print("Agent Graph:")
        self.agent.get_graph().print_ascii()

    def run_agent(self, user_input):
        self.agent_state = "RUNNING"
        inputs = {"messages":[("user", user_input)]}
        config = {"configurable": {"thread_id": self.thread_id}}
        result = self.agent.invoke(inputs, config=config)
        response = result['messages'][-1].content
        return response, result

    def resume_agent(self, user_input):
        self.agent_state = "RUNNING"
        config = {"configurable": {"thread_id": self.thread_id}}
        result = self.agent.invoke(
                Command(resume = user_input), 
                config=config)
        response = result['messages'][-1].content
        return response, result

