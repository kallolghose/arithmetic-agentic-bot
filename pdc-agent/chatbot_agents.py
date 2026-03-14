from langgraph.types import Command, interrupt
from langchain_core.tools import tool
from langchain.chat_models import init_chat_model
from dotenv import load_dotenv
import streamlit as st
from langgraph.checkpoint.memory import InMemorySaver
from agent_utilities import create_agent, run_agent, resume_agent

GLOBAL_STATE = []

# addition tool
@tool    # This identifies the following function as a tool to LangGraph
# in the following statement the function name, the attributes their types and the output type are defined
def addition(x:int, y:int) -> int : 
    # The following docstring describes what the function can do and is used by the LLM to determine whethere this
    # is the tool to be called, and what are its inputs and outputs
    """
    This addition function adds two numbers and returns their sum. 
    It takes two integers as its inputs and the output is an integer.
    """
    return x + y

# subtraction tool
@tool
def subtraction(x:int, y:int) -> int : 
    """
    This subtraction function subtracts a number from another and returns the difference. 
    It takes two integers as its inputs and the output is an integer.
    """
    return x - y
# multiplication tool
@tool
def multiplication(x:int, y:int) -> int : 
    """
    This multiplication function multiplies two numbers returns the product. 
    It takes two integers as its inputs and the output is an integer.
    """
    return x * y
# division tool
@tool
def division(x:int, y:int) -> int : 
    """
    This division function divides one number by another and returns the quotient. 
    It takes two integers as its inputs and the output is an integer.
    """
    return x / y

@tool
def human_assistance(query: str) -> str:
    """Ask human for input."""    
    st.session_state.messages.append({"role": "assistant", "content": query})
    st.session_state.agent_state="WAITING_FOR_HUMAN"
    interrupt({"query": query})

@tool
def get_weather(city: str) -> str:  
    """Get weather for a given city."""
    return f"It's always sunny in {city}!"


def clear_session_state():
    for key in st.session_state.keys():
        del st.session_state[key]

# Load environment variables from the .env file
load_dotenv()

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

if "uuid" not in st.session_state:
    import uuid
    st.session_state.threadId = str(uuid.uuid4())

if "agent_state" not in st.session_state:
    st.session_state.agent_state = ""

if "agent" not in st.session_state:
    # create agent
    st.session_state.agent = None

### What to be done via session state
if st.session_state.agent_state != "WAITING_FOR_HUMAN":
    model = init_chat_model(
        "openai:gpt-4o-mini",
        temperature=0
    )
    checkpointer = InMemorySaver()
    # Tool list
    arithmeticagent_tools = [addition, subtraction, multiplication, division, human_assistance]
    arithmeticagent_system_prompt = """You are a mathematics agent that can solve simple mathematics problems like addition, subtraction, multiplication and division. 
        Solve the mathematics problems provided by the user using only the available tools and not by yourself. Provide the answer given by the tool.  
        ## Validation Rules:
        1. Check for all the necessary natural numbers in the user query. If there are no numbers, ask the user to provide a valid mathematics question with numbers and for asking query use the human assistance tool.
        """
    # Agent Creation
    agent = create_agent(
        model=model,  
        tools=arithmeticagent_tools,  
        prompt=arithmeticagent_system_prompt,
        checkpointer=checkpointer,
        debug=False
    )
    st.session_state.agent = agent
    
agent = st.session_state.agent
st.title("Arithmetic Agent")
st.write("This is a simple chatbot that can answer simple mathematics questions using tools like addition, subtraction, multiplication and division.")

# Display chat messages from history on app re-run
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

detailed_yn = False

if prompt := st.chat_input("Enter a simple mathematics question"): # if input has a value
    with st.chat_message("user"):         # set the role as user
        st.markdown(prompt)               # display the message

    # We add the message to the chat history with the role as user
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("assistant"):    

        # Set the state of the agent
        if st.session_state.agent_state not in "WAITING_FOR_HUMAN":
            st.session_state.agent_state = "RUNNING"
            response, result = run_agent(agent, prompt, st.session_state.threadId)
        else:
            st.session_state.agent_state = "RUNNING"
            response, result = resume_agent(agent, prompt, st.session_state.threadId)

        # Detailed
        if detailed_yn:
            response = response + f"\nDetailed execution flow : \n"
            for message in result['messages']:
                response = response + "\n" + message.pretty_repr() + "\n"
        
        st_response = st.write(response)

    st.session_state.messages.append({"role": "assistant", "content": response})