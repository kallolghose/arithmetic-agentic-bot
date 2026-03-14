# main.py
from fastapi import FastAPI
from pydantic import BaseModel
from .agent_workflow import AgentWorkflow
from langchain.chat_models import init_chat_model
from langchain_ollama import ChatOllama
from langgraph.checkpoint.memory import InMemorySaver

app = FastAPI()

agent_details = {}

class QueryInput(BaseModel):
    query: str

@app.post("/initiate-chat")
async def process_query(input_data: QueryInput):
    import uuid
    _uuid = str(uuid.uuid4())
    agent_workflow = AgentWorkflow(thread_id=_uuid)

    # Run the LangGraph workflow
    # model = init_chat_model(
    #     "openai:gpt-4o-mini",
    #     temperature=0
    # )
    # Connect to ollama server
    model = ChatOllama(model="llama3.1", base_url="http://localhost:11434", temperature=0)
    checkpointer = InMemorySaver()
    # Tool list
    arithmeticagent_system_prompt = """You are a mathematics agent that can solve simple mathematics problems like addition, subtraction, multiplication and division.
        Use the tools provided. Once you get an answer from a tool, return it directly to the user and do not call any more tools.
        Also please perform the below validations:
        1. Ensure that the input is a valid mathematical operation.
        2. Ensure that the input is related to mathematics.
        If the input is not a valid mathematical operation or if the input is not related to mathematics, do not use any tool and instead use the human_assistance tool to ask for human assistance.
        """
    # ## Available Tools:
    #     1. addition: This addition function adds two numbers and returns the sum. It takes two integers as its inputs and the output is an integer.
    #     2. subtraction: This subtraction function subtracts a number from another and returns the difference
    #     3. multiplication: This multiplication function multiplies two numbers returns the product. It takes two integers as its inputs and the output is an integer.
    #     4. division: This division function divides one number by another and returns the quotient.
    #     5. human_assistance: This function is used to ask for human assistance when the query is not related to mathematics or if the input is not a valid mathematical operation.
    # Agent Creation
    agent_workflow.create_agent(
        model=model,  
        tools=[agent_workflow.addition, 
               agent_workflow.subtraction, 
               agent_workflow.multiplication, 
               agent_workflow.division, 
               agent_workflow.human_assistance],  # Pass bound methods
        prompt=arithmeticagent_system_prompt,
        checkpointer=checkpointer,
        debug=True
    )
    response, _ = agent_workflow.run_agent(input_data.query)
    agent_details[_uuid] = agent_workflow
    return {"thread_id": _uuid, "response": response}

@app.post("/resume-chat/{thread_id}")
async def resume_chat(thread_id: str, input_data: QueryInput):
    if thread_id not in agent_details:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Invalid thread ID")
    agent_workflow = agent_details[thread_id]
    response, _ = agent_workflow.resume_agent(input_data.query)
    return {"thread_id": thread_id, "response": response}

@app.get("/get-status/{thread_id}")
async def resume_chat(thread_id: str):
    if thread_id not in agent_details:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Invalid thread ID")
    return {"thread_id": thread_id, "status": agent_details.get(thread_id, {}).agent_state or  "NOT_FOUND"}