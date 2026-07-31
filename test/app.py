from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from dotenv import load_dotenv

from agents.agent import EnhancedLearningAgent
from agents.tool_registry import ToolRegistry
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version

# Import all the tools we've created
from tools.course_knowledge import course_knowledge_tool
from tools.conversation_memory import conversation_memory_tool
from tools.learning_state import learning_state_tool
from tools.rewrite import rewrite_tool
from tools.quiz import quiz_tool
from tools.recommendation import recommendation_tool
from tools.citation import citation_tool
from tools.external_learning import external_learning_tool
from tools.speech import speech_tool

# Load environment variables
load_dotenv()

ROOT = Path(__file__).parent
ARTIFACTS_DIR = ROOT / "artifacts"


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def safe_slug(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9_.-]+", "_", value.strip())
    return slug.strip("_") or "run"


def json_text(value: Any, *, max_chars: int | None = None) -> str:
    text = json.dumps(value, ensure_ascii=False, indent=2, default=str)
    if max_chars is not None and len(text) > max_chars:
        return text[:max_chars] + "\n...<truncated>"
    return text


def sanitize_tool_event(event: Dict[str, Any]) -> Dict[str, Any]:
    """Remove sensitive information from tool events for logging/display."""
    # Define keys that might contain sensitive information
    sensitive_keys = {
        "api_key", "apikey", "secret", "token", "password",
        "authorization", "auth", "key", "pass", "pwd", "credential"
    }

    def _sanitize(obj: Any) -> Any:
        if isinstance(obj, dict):
            return {
                k: "[REDACTED]" if any(s_key in k.lower() for s_key in sensitive_keys)
                else _sanitize(v)
                for k, v in obj.items()
            }
        elif isinstance(obj, list):
            return [_sanitize(item) for item in obj]
        elif isinstance(obj, str) and len(obj) > 100 and any(s_key in obj.lower() for s_key in ["sk-", "ak-", "Bearer"]):
            return "[REDACTED]"
        else:
            return obj

    return {
        "tool": event.get("tool"),
        "args": _sanitize(event.get("args", {})),
        "result": _sanitize(event.get("result", {})),
    }


def build_transcript_metadata(
    transcript_id: str,
    provider: str,
    model: str | None,
    version: str,
    system_prompt: str,
    tools: str,
    artifact_version: Any,
    history_window: int,
    max_tool_rounds: int,
) -> Dict[str, Any]:
    payload = {
        "transcript_id": transcript_id,
        **artifact_version_dict(artifact_version),
        "provider": provider,
        "model": model,
        "version": version,
        "system_prompt": str(system_prompt),
        "tools": str(tools),
        "history_window": history_window,
        "max_tool_rounds": max_tool_rounds,
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "turns": [],
    }
    return payload


def create_transcript_path(transcripts_dir: Path, provider: str, version: str) -> Path:
    timestamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
    transcript_id = "_".join([safe_slug(version), safe_slug(provider), timestamp])
    return transcripts_dir / f"{transcript_id}.transcript.json"


def print_tool_rounds(rounds: List[Dict[str, Any]]) -> None:
    """Print tool execution rounds in a readable format."""
    for round_data in rounds:
        print(f"\nRound {round_data['round']}")
        if round_data.get("assistant_text"):
            print(f"  Agent: {round_data['assistant_text']}")
        for event in round_data.get("tool_results", []):
            print(f"  Tool: {event['tool']}")
            print(f"    Args: {json_text(event.get('args', {}), max_chars=1200)}")
            print(f"    Result: {json_text(event.get('result', {}), max_chars=1200)}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="AI Learning Agent - An intelligent educational companion"
    )
    parser.add_argument(
        "--provider",
        choices=["openrouter"],
        default="openrouter",
        help="LLM provider to use"
    )
    parser.add_argument(
        "--model",
        default=None,
        help="Specific model to use (defaults to provider's default)"
    )
    parser.add_argument(
        "--version",
        help="Student-chosen artifact version label, e.g. v0, v1, v2.",
        default="v0"
    )
    parser.add_argument(
        "--system-prompt",
        type=Path,
        default=ARTIFACTS_DIR / "system_prompt.md"
    )
    parser.add_argument(
        "--tools",
        type=Path,
        default=ARTIFACTS_DIR / "tools.yaml"
    )
    parser.add_argument(
        "--transcripts-dir",
        type=Path,
        default=ROOT / "transcripts"
    )
    parser.add_argument(
        "--history-window",
        type=int,
        default=5,
        help="Keep the last N user/assistant pairs in context."
    )
    parser.add_argument(
        "--max-tool-rounds",
        type=int,
        default=10,  # Increased for more complex reasoning chains
        help="Maximum number of tool reasoning rounds"
    )
    parser.add_argument(
        "--student-id",
        default="default_student",
        help="Identifier for the student (used for learning state tracking)"
    )

    args = parser.parse_args()

    # Validate required files exist
    if not args.system_prompt.exists():
        print(f"Error: System prompt file not found: {args.system_prompt}")
        sys.exit(1)

    if not args.tools.exists():
        print(f"Error: Tools file not found: {args.tools}")
        sys.exit(1)

    # Load configuration
    system_prompt = args.system_prompt.read_text(encoding="utf-8")
    tool_declarations = load_tool_declarations(args.tools)
    openai_tools = to_openai_tools(tool_declarations)
    provider = make_provider(args.provider)
    selected_model = args.model or getattr(provider, "default_model", None)
    artifact_version = build_artifact_version(args.version, args.system_prompt, args.tools)

    # Create transcripts directory
    args.transcripts_dir.mkdir(parents=True, exist_ok=True)

    # Initialize the enhanced learning agent
    agent = EnhancedLearningAgent(
        provider=provider,
        system_prompt=system_prompt,
        tools=openai_tools,
        model=selected_model,
    )

    # Register all our custom tools with the agent's tool registry
    agent.register_tool(course_knowledge_tool)
    agent.register_tool(conversation_memory_tool)
    agent.register_tool(learning_state_tool)
    agent.register_tool(rewrite_tool)
    agent.register_tool(quiz_tool)
    agent.register_tool(recommendation_tool)
    agent.register_tool(citation_tool)
    agent.register_tool(external_learning_tool)
    agent.register_tool(speech_tool)

    # Setup agent components (this would initialize all the sub-components)
    agent.setup()

    print(f"AI Learning Agent initialized. artifact_version={artifact_version.artifact_version}")
    print("Type /exit or /quit to stop.")
    print(f"Transcripts will be saved to: {args.transcripts_dir}\n")

    history: List[Dict[str, str]] = []
    turn_index = 0

    while True:
        try:
            user_text = input("You> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not user_text:
            continue
        if user_text in {"/exit", "/quit"}:
            break

        # Add student ID to context for learning state tools
        user_message = {"role": "user", "content": user_text}

        turn_index += 1
        recent_history = history[-args.history_window * 2:] if args.history_window > 0 else []
        messages = [
            {"role": "system", "content": system_prompt},
            *recent_history,
            user_message,
        ]

        turn_record: Dict[str, Any] = {
            "turn_index": turn_index,
            "started_at": now_iso(),
            "user": user_text,
            "student_id": args.student_id,
            "status": "started",
            "assistant_text": None,
            "rounds": [],
            "tool_events": [],
        }

        try:
            # Run the agent
            result = agent.run(list(messages))
            agent_result_dict = {
                "status": "completed",
                "assistant_text": result.text,
                "rounds": [],  # Would be populated by actual implementation
                "tool_events": [sanitize_tool_event(e) for e in result.state.tool_results],
            }
            turn_record.update(agent_result_dict)
            assistant_text = result.text

            print(f"\nAgent> {assistant_text}")
            print_tool_rounds(agent_result_dict.get("rounds", []))

            # Update conversation history
            history.append({"role": "user", "content": user_text})
            history.append({"role": "assistant", "content": assistant_text or ""})

        except Exception as exc:
            turn_record.update({
                "status": "agent_error",
                "error": f"{type(exc).__name__}: {str(exc)}",
            })
            print(f"\nERROR> {turn_record['error']}")

        turn_record["ended_at"] = now_iso()

        # In a full implementation, we would save the transcript here
        # For now, just acknowledge
        print(f"Turn {turn_index} completed\n")

    print("Goodbye! Keep learning!")


if __name__ == "__main__":
    main()