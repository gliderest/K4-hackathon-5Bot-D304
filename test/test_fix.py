#!/usr/bin/env python3
"""Test script to verify the AgentRun fix"""

from agents.agent import EnhancedLearningAgent
from agents.tool_registry import ToolRegistry
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import build_artifact_version
from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

# Load configuration
ROOT = Path(__file__).parent
ARTIFACTS_DIR = ROOT / "artifacts"

# Load tool declarations and convert to OpenAI format
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

# Test the agent run
test_messages = [{"role": "user", "content": "Hello, this is a test message."}]

print("Testing agent run...")
try:
    agent_run = agent.run(test_messages)
    print(f"Agent run successful!")
    print(f"Response text: {agent_run.text}")
    print(f"Tool calls count: {len(agent_run.tool_calls)}")
    print(f"Tool results count: {len(agent_run.tool_results)}")

    # Test accessing the attributes we're now using in server.py
    print(f"Text attribute accessible: {agent_run.text is not None}")
    print(f"Tool calls accessible: {len(agent_run.tool_calls)}")
    print(f"Tool results accessible: {len(agent_run.tool_results)}")

    # Test the specific code we fixed
    agent_state_dict = {
        "text": agent_run.text,
        "tool_calls": [{"name": tc.name, "args": tc.args} for tc in agent_run.tool_calls],
        "tool_results": agent_run.tool_results
    }
    print(f"Agent state dict created successfully: {type(agent_state_dict)}")

    print("\n✅ Fix verification successful!")

except Exception as e:
    print(f"❌ Error during agent run: {e}")
    import traceback
    traceback.print_exc()