
from langgraph.prebuilt import create_react_agent
from langchain.chat_models import init_chat_model

def get_weather(city: str) -> str:  
    """Get weather for a given city."""
    return f"It's always sunny in {city}!"


def main():
    model = init_chat_model(
        "openai:gpt-4o-mini",
        temperature=0
    )
    agent = create_react_agent(
        model=model,  
        tools=[get_weather],  
        prompt="You are a helpful assistant"  
    )
    print("Agent Graph:")
    agent.get_graph().print_ascii()

    # Run the agent
    result = agent.invoke(
        {"messages": [{"role": "user", "content": "what is the weather in sf"}]}
    )
    response = result['messages'][-1].content
    print("Response:", response)

if __name__ == "__main__":
    main()
