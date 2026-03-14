# pdc-langgraph-chatbot

Lightweight chatbot project using LangGraph/LangChain with a Streamlit front-end and a FastAPI backend.

## Project layout (important files)
- `pdc-agent/` — Streamlit app and agent tools (Streamlit UI).
  - `chatbot_agents.py` — main Streamlit chat UI (run with Streamlit).
  - other agent/tool modules.
- `api/` — FastAPI server and agent workflow.
  - `api_server.py` — FastAPI app (uvicorn entry target).
  - `agent_workflow.py` — agent class and tool definitions.
- `.env` — environment variables (not committed).
- `requirements.txt` — Python dependencies (create if missing).

## Prerequisites
- Python 3.10+ recommended
- Windows machine (commands below use PowerShell / CMD)
- Optional: Ollama running locally if using `ChatOllama`

## Quick setup (Windows PowerShell)
1. Create and activate virtual environment:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
   Or for CMD:
   ```
   .venv\Scripts\activate.bat
   ```

2. Install dependencies:
   - If you have `requirements.txt`:
     ```
     pip install -r requirements.txt
     ```
   - Example minimal packages you may need:
     ```
     pip install fastapi "uvicorn[standard]" streamlit python-dotenv langchain langgraph langchain-ollama
     ```
   Adjust package names/versions as required by your project.

3. Create a `.env` file in the project root (if not present) and add variables your app needs:
   ```
   OPENAI_API_KEY=sk-...
   OLLAMA_URL=http://localhost:11434
   OTHER_VAR=value
   ```
   The code uses `python-dotenv` (`load_dotenv()`), so these values will be loaded automatically if present.

## Run the FastAPI backend (uvicorn)
From the project root run:
```powershell
uvicorn api.api_server:app --reload --port 8000
```
- This exposes the API at `http://127.0.0.1:8000`.
- Use `--reload` during development.

If your FastAPI entry is in a different module path, adjust `api.api_server:app` accordingly.

## Run the Streamlit front-end
Open a second terminal (activate the same virtualenv) and run:
```powershell
streamlit run pdc-agent/chatbot_agents.py
```
- Streamlit UI opens in the browser (default `http://localhost:8501`).
- If your Streamlit main file has a different name, replace the path accordingly.

## Running both together
- Start uvicorn in terminal A.
- Start Streamlit in terminal B.
- The Streamlit app will call the backend or directly invoke the agent depending on configuration.

## Common notes / troubleshooting
- Tools must be registered as bound methods. Pass instance methods (e.g., `agent.addition`) when creating the agent.
- Do not call Streamlit UI functions from background threads or tool functions. Use `st.session_state` to pass data from threads/tools to the main script and render UI there to avoid `missing ScriptRunContext` warnings.
- If the agent loops and you get `GRAPH_RECURSION_LIMIT`, make the prompt explicit about stopping conditions and ensure tool outputs are final answers (no instructions that re-trigger the agent).
- To view the internal agent graph after creation:
  ```python
  agent.get_graph().print_ascii()
  # or get SVG:
  svg = agent.get_graph().print_svg()
  ```
- If you use Ollama: ensure the Ollama server is running and `OLLAMA_URL` (or equivalent) matches.

## Debugging & logs
- Add logging in `agent_workflow.py` and tools to trace execution.
- Add print or logger statements before/after `agent.invoke()` to inspect messages and state returned by the agent.

## Example commands summary
PowerShell:
```powershell
# setup
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# run backend
uvicorn api.api_server:app --reload --port 8000

# run front-end (in a second terminal)
streamlit run pdc-agent/chatbot_agents.py
```

CMD:
```
.venv\Scripts\activate.bat
pip install -r requirements.txt
uvicorn api.api_server:app --reload --port 8000
streamlit run pdc-agent/chatbot_agents.py
```

If further details are required (requirements file, sample `.env`, or exact Streamlit entry point), provide the filenames and a short description and the README can be updated