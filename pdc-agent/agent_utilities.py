from langchain_core.tools import tool
import streamlit as st
from langgraph.types import Command

def create_agent(model, tools, prompt, checkpointer=None, debug=False):
    from langgraph.prebuilt import create_react_agent
    return create_react_agent(
    model = model,
    prompt = prompt,
    tools = tools,
    checkpointer=checkpointer,
    debug = debug)


def run_agent(agent, user_input, thread_id):
    inputs = {"messages":[("user", user_input)]}
    config = {"configurable": {"thread_id": thread_id}}
    result = agent.invoke(inputs, config=config)
    response = result['messages'][-1].content
    return response, result

def resume_agent(agent, user_input, thread_id):
    config = {"configurable": {"thread_id": thread_id}}
    result = agent.invoke(
            Command(resume = user_input), 
            config=config)
    response = result['messages'][-1].content
    return response, result