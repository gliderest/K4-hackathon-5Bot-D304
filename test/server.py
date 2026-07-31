from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import uvicorn

from agents.agent import EnhancedLearningAgent
from agents.tool_registry import ToolRegistry
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import build_artifact_version
from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI(title="AI Learning Agent API")

# Configure CORS so frontend running on another port can communicate with API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the agent (similar to app.py but for API)
ROOT = Path(__file__).parent
ARTIFACTS_DIR = ROOT / "artifacts"

# Load tool declarations and convert to OpenAI format (though we might not need it for direct tool calls)
tool_declarations = load_tool_declarations(ARTIFACTS_DIR / "tools.yaml")
openai_tools = to_openai_tools(tool_declarations)

# Create provider
provider = make_provider("openrouter")  # defaults to openrouter
model = None  # use provider's default

# Build agent version (optional)
artifact_version = build_artifact_version("v0", ARTIFACTS_DIR / "system_prompt.md", ARTIFACTS_DIR / "tools.yaml")

# Load system prompt
system_prompt = (ARTIFACTS_DIR / "system_prompt.md").read_text(encoding="utf-8")

# Create the agent
agent = EnhancedLearningAgent(
    provider=provider,
    system_prompt=system_prompt,
    tools=openai_tools,
    model=model
)

# Register all tools (same as in app.py)
from tools.course_knowledge import course_knowledge_tool
from tools.conversation_memory import conversation_memory_tool
from tools.learning_state import learning_state_tool
from tools.rewrite import rewrite_tool
from tools.quiz import quiz_tool
from tools.recommendation import recommendation_tool
from tools.citation import citation_tool
from tools.external_learning import external_learning_tool
from tools.speech import speech_tool

agent.register_tool(course_knowledge_tool)
agent.register_tool(conversation_memory_tool)
agent.register_tool(learning_state_tool)
agent.register_tool(rewrite_tool)
agent.register_tool(quiz_tool)
agent.register_tool(recommendation_tool)
agent.register_tool(citation_tool)
agent.register_tool(external_learning_tool)
agent.register_tool(speech_tool)

# Setup the agent (registers tools, etc.)
agent.setup()

# In-memory storage for chat sessions (in production, use a database or Redis)
sessions: Dict[str, Any] = {}

class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"
    context: Optional[Dict[str, Any]] = None  # e.g., {"current_lesson": "...", "current_page": 1}

class ChatResponse(BaseModel):
    response: str
    session_id: str

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Handle a chat message from the frontend.
    """
    # Get or create session state
    if request.session_id not in sessions:
        sessions[request.session_id] = {
            "history": [],  # list of {"role": "user"/"assistant", "content": str}
            "agent_state": None
        }

    session = sessions[request.session_id]

    # Prepare user message
    user_message = request.message

    # If context is provided, we can prepend it to the message for the agent
    if request.context:
        context_str = f"Current context: Lesson: {request.context.get('current_lesson', 'Unknown')}, Page: {request.context.get('current_page', 1)}. "
        user_message = context_str + user_message

    # Add user message to history
    session["history"].append({"role": "user", "content": user_message})

    # Prepare messages for the agent (system + history)
    messages = [{"role": "system", "content": system_prompt}] + session["history"]

    # Run the agent
    try:
        agent_run = agent.run(messages)
        assistant_response = agent_run.text or ""

        # Add assistant response to history
        session["history"].append({"role": "assistant", "content": assistant_response})

        # Update session state (if needed) - store the agent run results
        session["agent_state"] = {
            "text": agent_run.text,
            "tool_calls": [{"name": tc.name, "args": tc.args} for tc in agent_run.tool_calls],
            "tool_results": agent_run.tool_results
        }

        return ChatResponse(
            response=assistant_response,
            session_id=request.session_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)