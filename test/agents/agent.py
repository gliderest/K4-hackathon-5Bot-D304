from __future__ import annotations

from typing import Any, Dict, List, Optional

from .base import LearningAgent, AgentState, AgentRun
from .planner import Planner, Plan, Task
from .tool_registry import ToolRegistry, Tool
from providers.base import Provider, ModelResponse


class EnhancedLearningAgent(LearningAgent):
    """
    Enhanced Learning Agent that implements the full AI Learning Architecture
    with Intent Detection, Planning, Tool Calling Loop, Context Building,
    Reflection, and Confidence Checking.
    """

    def __init__(
        self,
        provider: Provider,
        *,
        system_prompt: str,
        tools: List[Dict[str, Any]] | None = None,
        model: str | None = None,
    ) -> None:
        super().__init__(provider, system_prompt=system_prompt, tools=tools, model=model)

        # Initialize components
        self.planner = Planner()
        self.tool_registry = ToolRegistry()
        # These would be implemented as separate classes in a full implementation
        self.intent_detector = None  # Placeholder for intent detection
        self.context_builder = None  # Placeholder for context building
        self.reflection_engine = None  # Placeholder for reflection
        self.confidence_checker = None  # Placeholder for confidence checking

    def setup(self) -> None:
        """Initialize all components. Register tools here."""
        # In a full implementation, we would initialize:
        # self.intent_detector = IntentDetector()
        # self.context_builder = ContextBuilder()
        # self.reflection_engine = ReflectionEngine()
        # self.confidence_checker = ConfidenceChecker()

        # For now, we'll focus on having the planner and tool registry work
        pass

    def register_tool(self, tool: Tool) -> None:
        """Register a tool with the agent's tool registry."""
        self.tool_registry.register(tool)

    def register_tool_class(self, tool_class: type) -> None:
        """Register a tool class for lazy instantiation."""
        self.tool_registry.register_class(tool_class)

    def run(self, user_messages: List[Dict[str, str]]) -> AgentRun:
        """Main execution loop implementing the learning agent workflow."""
        # Initialize state
        state = AgentState()
        state.messages = [{"role": "system", "content": self.system_prompt}, *user_messages]

        # Step 1: Intent Detection
        if self.intent_detector:
            state.intent = self.intent_detector.detect(state.messages)
        else:
            # Fallback intent detection (simplified)
            state.intent = self._simple_intent_detection(state.messages)

        # Step 2: Planning
        if self.planner:
            state.plan = self.planner.create_plan(
                state.intent or {},
                state,
                self.tools or []
            )
            # Step 2.5: Task Decomposition (using planner's capability)
            if hasattr(self.planner, 'decompose_to_plan'):  # We'll add this method
                # For now, we'll use a simple approach
                pass

        # Convert plan to executable tasks using tool registry
        executable_tasks = self._plan_to_tasks(state.plan) if state.plan else []

        # Step 3: Tool Calling Loop (enhanced version with task execution)
        tool_results = self._execute_task_loop(executable_tasks, state)
        state.tool_results = tool_results

        # Step 4: Context Building
        if self.context_builder and tool_results:
            state.context = self.context_builder.build_context(
                state.messages,
                state.tool_results,
                state.intent,
                getattr(self, 'task_decomposer', None)
            )
        else:
            # Simple context building fallback
            state.context = self._build_simple_context(state.messages, state.tool_results)

        # Step 5: LLM Reasoning
        if state.context:
            state.messages.append({
                "role": "user",
                "content": f"Based on the following context, provide a helpful educational response:\n\n{state.context}"
            })

        response = self.provider.complete(
            state.messages,
            self.tools,
            model=self.model,
            temperature=0.0,
        )
        state.response = response.text

        # Step 6: Reflection
        if self.reflection_engine and state.response:
            state.reflection = self.reflection_engine.reflect(
                state.response,
                state.messages[0]["content"] if state.messages else "",  # original query
                state.tool_results,
                state
            )

            # If reflection suggests issues and we haven't tried too many times, we might iterate
            reflection_attempts = getattr(state, 'reflection_attempts', 0)
            if state.reflection.get("needs_improvement", False) and reflection_attempts < 2:
                state.reflection_attempts = reflection_attempts + 1
                # Add reflection feedback and retry (simplified)
                feedback = state.reflection.get("feedback", "")
                state.messages.append({
                    "role": "user",
                    "content": f"Previous response could be improved: {feedback}. Please provide a better response."
                })

                # Recursive call with depth limit
                if reflection_attempts < 1:  # Prevent infinite recursion
                    return self.run(user_messages)  # Simplified retry

        # Step 7: Confidence Checking
        if self.confidence_checker and state.response:
            confidence_result = self.confidence_checker.check(
                state.response,
                state.tool_results,
                state.reflection or {}
            )
            state.confidence = confidence_result.get("score", 1.0)

            # If confidence is low and we haven't tried to improve, attempt improvement
            if state.confidence and state.confidence < 0.7:
                improvement_attempts = getattr(state, 'improvement_attempts', 0)
                if improvement_attempts < 1:  # Limit improvement attempts
                    state.improvement_attempts = improvement_attempts + 1
                    # In a full implementation, we would use the confidence feedback
                    # to guide additional tool use or refinement

        return AgentRun(
            text=state.response, 
            tool_results=state.tool_results,
            tool_calls=[], # Add tool_calls here if you extract them, or leave empty if not used
            state=state
        )

    def _simple_intent_detection(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """Simple fallback intent detection based on keywords."""
        if not messages:
            return {"type": "unknown", "goal": ""}

        # Get the latest user message
        user_message = ""
        for msg in reversed(messages):
            if msg["role"] == "user":
                user_message = msg["content"]
                break

        user_message_lower = user_message.lower()

        # Simple keyword-based intent detection
        if any(word in user_message_lower for word in ["explain", "what is", "how does", "why", "describe"]):
            intent_type = "explain_concept"
        elif any(word in user_message_lower for word in ["compare", "difference", "versus", "vs", "better"]):
            intent_type = "compare_concepts"
        elif any(word in user_message_lower for word in ["summarize", "summary", "tl;dr", "brief"]):
            intent_type = "summarize_material"
        elif any(word in user_message_lower for word in ["quiz", "question", "test", "practice"]):
            intent_type = "generate_quiz"
        elif any(word in user_message_lower for word in ["recommend", "suggest", "next", "should i study"]):
            intent_type = "get_recommendation"
        else:
            intent_type = "general_question"

        # Extract entities (very simplified)
        entities = {}
        # In reality, we'd use NER or more sophisticated extraction

        return {
            "type": intent_type,
            "goal": user_message,
            "entities": entities
        }

    def _plan_to_tasks(self, plan) -> List[dict]:
        """Convert a plan object to executable task dictionaries."""
        tasks = []
        if hasattr(plan, 'tasks'):
            for i, task in enumerate(plan.tasks):
                task_dict = {
                    "id": getattr(task, 'id', f"task_{i}"),
                    "description": getattr(task, 'description', str(task)),
                    "tool_name": getattr(task, 'tool_name', ""),
                    "tool_args": getattr(task, 'tool_args', {}),
                    "dependencies": getattr(task, 'dependencies', []),
                }
                tasks.append(task_dict)
        return tasks

    def _execute_task_loop(self, tasks: List[dict], state: AgentState) -> List[Dict[str, Any]]:
        """Execute tasks in order, respecting dependencies."""
        results = []
        completed_tasks = set()

        # Simple topological sort for dependency resolution
        # In a real implementation, we'd use a proper topological sort
        remaining_tasks = tasks.copy()

        while remaining_tasks:
            # Find tasks with no unmet dependencies
            ready_tasks = []
            for task in remaining_tasks:
                deps_met = all(dep in completed_tasks for dep in task.get("dependencies", []))
                if deps_met:
                    ready_tasks.append(task)

            if not ready_tasks:
                # Circular dependency or missing dependency - execute what we can
                # In production, we'd handle this more gracefully
                if remaining_tasks:
                    ready_tasks = [remaining_tasks[0]]  # Take first to avoid infinite loop
                else:
                    break

            # Execute ready tasks
            tasks_to_remove = []
            for task in ready_tasks:
                result = self._execute_single_task(task)
                results.append(result)

                # Mark as completed
                completed_tasks.add(task["id"])
                tasks_to_remove.append(task)

            # Remove completed tasks from remaining_tasks
            for task in tasks_to_remove:
                remaining_tasks.remove(task)

        return results

    def _execute_single_task(self, task: dict) -> Dict[str, Any]:
        """Execute a single task using the tool registry."""
        tool_name = task.get("tool_name")
        tool_args = task.get("tool_args", {})

        if not tool_name:
            return {
                "tool": "unknown",
                "args": {},
                "result": {"error": "invalid_task", "message": "Task missing tool_name"}
            }

        tool_instance = self.tool_registry.get(tool_name)
        if not tool_instance:
            return {
                "tool": tool_name,
                "args": tool_args,
                "result": {"error": "tool_not_found", "message": f"No tool registered with name '{tool_name}'"}
            }

        try:
            result = tool_instance.execute(**tool_args)
            return {
                "tool": tool_name,
                "args": tool_args,
                "result": result
            }
        except Exception as e:
            return {
                "tool": tool_name,
                "args": tool_args,
                "result": {"error": type(e).__name__, "message": str(e)}
            }

    def _build_simple_context(self, messages: List[Dict[str, str]], tool_results: List[Dict[str, Any]]) -> str:
        """Build a simple context from tool results when context builder is not available."""
        context_parts = ["# Available Information\n"]

        if tool_results:
            context_parts.append("## Tool Results:")
            for i, result in enumerate(tool_results, 1):
                tool_name = result.get("tool", "unknown")
                result_data = result.get("result", {})
                context_parts.append(f"\n### {tool_name} Result {i}:\n{self._format_result(result_data)}")
        else:
            context_parts.append("No tool results available.")

        return "\n".join(context_parts)

    def _format_result(self, result: Any) -> str:
        """Format a result for inclusion in context."""
        if isinstance(result, dict):
            if "error" in result:
                return f"Error: {result.get('message', 'Unknown error')}"
            # Try to extract meaningful information
            formatted_parts = []
            for key, value in result.items():
                if key not in ["error", "tool", "args"]:
                    formatted_parts.append(f"- {key}: {value}")
            return "\n".join(formatted_parts) if formatted_parts else str(result)
        elif isinstance(result, list):
            if not result:
                return "Empty list"
            formatted_items = []
            for i, item in enumerate(result[:5]):  # Limit to first 5 items
                formatted_items.append(f"{i+1}. {self._format_result(item)}")
            if len(result) > 5:
                formatted_items.append(f"... and {len(result) - 5} more items")
            return "\n".join(formatted_items)
        else:
            return str(result)