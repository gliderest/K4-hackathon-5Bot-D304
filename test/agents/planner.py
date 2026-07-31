from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .base import AgentState


@dataclass
class Task:
    """Represents a task to be executed by the agent."""
    id: str
    description: str
    tool_name: str
    tool_args: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)  # Task IDs this task depends on
    completed: bool = False
    result: Any = None


@dataclass
class Plan:
    """Represents an execution plan consisting of multiple tasks."""
    goal: str
    tasks: List[Task] = field(default_factory=list)
    completed_tasks: List[str] = field(default_factory=list)
    failed_tasks: List[str] = field(default_factory=list)


class Planner:
    """
    Responsible for creating execution plans based on user intent and current state.
    The planner breaks down high-level goals into specific tasks that can be executed
    by calling appropriate tools.
    """

    def __init__(self) -> None:
        # In a more sophisticated implementation, this might use LLMs or rule-based systems
        pass

    def create_plan(
        self,
        intent: Dict[str, Any],
        agent_state: AgentState,
        available_tools: List[Dict[str, Any]]
    ) -> Plan:
        """
        Create an execution plan based on user intent and current agent state.

        Args:
            intent: Detected user intent from intent detection component
            agent_state: Current state of the agent
            available_tools: List of available tool definitions

        Returns:
            Plan: An execution plan with tasks to accomplish the goal
        """
        # Extract key information from intent
        goal = intent.get("goal", "")
        intent_type = intent.get("type", "unknown")
        entities = intent.get("entities", {})

        # Create plan
        plan = Plan(goal=goal)

        # Simple rule-based planning based on intent type
        # In a production system, this would be more sophisticated
        if intent_type == "explain_concept":
            plan = self._plan_explain_concept(entities, agent_state, available_tools)
        elif intent_type == "compare_concepts":
            plan = self._plan_compare_concepts(entities, agent_state, available_tools)
        elif intent_type == "summarize_material":
            plan = self._plan_summarize_material(entities, agent_state, available_tools)
        elif intent_type == "generate_quiz":
            plan = self._plan_generate_quiz(entities, agent_state, available_tools)
        elif intent_type == "get_recommendation":
            plan = self._plan_get_recommendation(entities, agent_state, available_tools)
        else:
            # Default planning strategy
            plan = self._plan_default(goal, entities, agent_state, available_tools)

        return plan

    def _plan_explain_concept(
        self,
        entities: Dict[str, Any],
        agent_state: AgentState,
        available_tools: List[Dict[str, Any]]
    ) -> Plan:
        """Create a plan for explaining a concept."""
        concept = entities.get("concept", "")
        difficulty = entities.get("difficulty", "adaptive")

        plan = Plan(goal=f"Explain the concept of {concept}")

        # Task 1: Check learning state to understand student's current knowledge
        plan.tasks.append(Task(
            id="check_learning_state",
            description=f"Check current knowledge level for {concept}",
            tool_name="learning_state",
            tool_args={
                "operation": "get",
                "student_id": agent_state.state.get("student_id", "default_student") if hasattr(agent_state, 'state') else "default_student",
                "topic": concept
            }
        ))

        # Task 2: Retrieve relevant course materials
        plan.tasks.append(Task(
            id="retrieve_course_knowledge",
            description=f"Get information about {concept} from course materials",
            tool_name="course_knowledge",
            tool_args={
                "query": concept,
                "source_priority": "current_lesson",  # Start with current lesson
                "max_results": 5
            }
        ))

        # Task 3: Check conversation memory for prior explanations
        plan.tasks.append(Task(
            id="check_conversation_memory",
            description=f"Check if we've explained {concept} before",
            tool_name="conversation_memory",
            tool_args={
                "operation": "search",
                "query": concept,
                "limit": 5
            }
        ))

        # Task 4: Synthesize explanation (this would be done by the LLM after gathering info)
        # Task 5: Check if explanation needs simplification based on learning state
        plan.tasks.append(Task(
            id="adjust_explanation",
            description=f"Adjust explanation complexity based on student level",
            tool_name="rewrite",
            tool_args={
                "style": "simplify" if difficulty == "beginner" else "expand",
                "target_audience": difficulty
            },
            dependencies=["check_learning_state", "retrieve_course_knowledge", "check_conversation_memory"]
        ))

        return plan

    def _plan_compare_concepts(
        self,
        entities: Dict[str, Any],
        agent_state: AgentState,
        available_tools: List[Dict[str, Any]]
    ) -> Plan:
        """Create a plan for comparing two concepts."""
        concept1 = entities.get("concept1", "")
        concept2 = entities.get("concept2", "")

        plan = Plan(goal=f"Compare {concept1} and {concept2}")

        # Get both concepts
        plan.tasks.append(Task(
            id="get_concept1_info",
            description=f"Get information about {concept1}",
            tool_name="course_knowledge",
            tool_args={
                "query": concept1,
                "source_priority": "current_lesson",
                "max_results": 5
            }
        ))

        plan.tasks.append(Task(
            id="get_concept2_info",
            description=f"Get information about {concept2}",
            tool_name="course_knowledge",
            tool_args={
                "query": concept2,
                "source_priority": "current_lesson",
                "max_results": 5
            }
        ))

        # Compare concepts (would be done by LLM)
        plan.tasks.append(Task(
            id="compare_concepts",
            description=f"Compare {concept1} and {concept2}",
            tool_name="rewrite",  # Using rewrite for comparison/synthesis
            tool_args={
                "content": "",  # Would be filled with actual content from previous tasks
                "style": "compare",
                "target_audience": "general"
            },
            dependencies=["get_concept1_info", "get_concept2_info"]
        ))

        return plan

    def _plan_summarize_material(
        self,
        entities: Dict[str, Any],
        agent_state: AgentState,
        available_tools: List[Dict[str, Any]]
    ) -> Plan:
        """Create a plan for summarizing course material."""
        topic = entities.get("topic", "")
        length = entities.get("length", "medium")

        plan = Plan(goal=f"Summarize material on {topic}")

        # Get the material to summarize
        plan.tasks.append(Task(
            id="get_material",
            description=f"Get material on {topic} for summarization",
            tool_name="course_knowledge",
            tool_args={
                "query": topic,
                "source_priority": "current_lesson",
                "max_results": 10  # Get more content for summarization
            }
        ))

        # Summarize the material
        plan.tasks.append(Task(
            id="summarize_content",
            description=f"Summarize the material on {topic}",
            tool_name="rewrite",
            tool_args={
                "style": "summarize",
                "target_audience": "general"
            },
            dependencies=["get_material"]
        ))

        return plan

    def _plan_generate_quiz(
        self,
        entities: Dict[str, Any],
        agent_state: AgentState,
        available_tools: List[Dict[str, Any]]
    ) -> Plan:
        """Create a plan for generating quiz questions."""
        topic = entities.get("topic", "")
        question_count = entities.get("count", 5)
        question_type = entities.get("type", "mixed")

        plan = Plan(goal=f"Generate quiz questions on {topic}")

        # Check learning state to determine appropriate difficulty
        plan.tasks.append(Task(
            id="assess_level",
            description="Assess student's current level for appropriate question difficulty",
            tool_name="learning_state",
            tool_args={
                "operation": "get",
                "student_id": agent_state.state.get("student_id", "default_student") if hasattr(agent_state, 'state') else "default_student",
                "topic": topic
            }
        ))

        # Get relevant material for question generation
        plan.tasks.append(Task(
            id="get_quiz_material",
            description=f"Get material on {topic} for creating questions",
            tool_name="course_knowledge",
            tool_args={
                "query": topic,
                "source_priority": "current_lesson",
                "max_results": 8
            }
        ))

        # Generate quiz questions
        plan.tasks.append(Task(
            id="generate_questions",
            description=f"Generate {question_count} {question_type} questions on {topic}",
            tool_name="quiz",
            tool_args={
                "topic": topic,
                "question_type": question_type,
                "count": question_count,
                "difficulty": "adaptive"  # Will be adjusted based on assessment
            },
            dependencies=["assess_level", "get_quiz_material"]
        ))

        return plan

    def _plan_get_recommendation(
        self,
        entities: Dict[str, Any],
        agent_state: AgentState,
        available_tools: List[Dict[str, Any]]
    ) -> Plan:
        """Create a plan for getting learning recommendations."""
        rec_type = entities.get("type", "next_topic")
        current_topic = entities.get("topic", "")

        plan = Plan(goal=f"Get {rec_type} recommendation")

        plan.tasks.append(Task(
            id="get_recommendation",
            description=f"Get {rec_type} recommendation for student",
            tool_name="recommendation",
            tool_args={
                "student_id": agent_state.state.get("student_id", "default_student") if hasattr(agent_state, 'state') else "default_student",
                "recommendation_type": rec_type,
                "current_topic": current_topic
            }
        ))

        return plan

    def _plan_default(
        self,
        goal: str,
        entities: Dict[str, Any],
        agent_state: AgentState,
        available_tools: List[Dict[str, Any]]
    ) -> Plan:
        """Default planning strategy when intent type is not recognized."""
        plan = Plan(goal=goal)

        # General approach: check learning state, get relevant info, then respond
        topic = entities.get("topic", goal)  # Fallback to goal as topic

        plan.tasks.append(Task(
            id="check_learning_state",
            description="Check current learning state",
            tool_name="learning_state",
            tool_args={
                "operation": "get",
                "student_id": agent_state.state.get("student_id", "default_student") if hasattr(agent_state, 'state') else "default_student",
                "topic": topic
            }
        ))

        plan.tasks.append(Task(
            id="get_relevant_knowledge",
            description=f"Get relevant knowledge about {topic}",
            tool_name="course_knowledge",
            tool_args={
                "query": topic,
                "source_priority": "current_lesson",
                "max_results": 5
            }
        ))

        return plan

    def get_next_executable_tasks(self, plan: Plan) -> List[Task]:
        """
        Get tasks that are ready to be executed (dependencies satisfied).

        Args:
            plan: The execution plan

        Returns:
            List[Task]: Tasks that can be executed now
        """
        ready_tasks = []
        completed_task_ids = set(plan.completed_tasks)

        for task in plan.tasks:
            if task.completed:
                continue

            # Check if all dependencies are completed
            dependencies_met = all(dep in completed_task_ids for dep in task.dependencies)

            if dependencies_met:
                ready_tasks.append(task)

        return ready_tasks

    def mark_task_completed(self, plan: Plan, task_id: str, result: Any = None) -> None:
        """
        Mark a task as completed in the plan.

        Args:
            plan: The execution plan
            task_id: ID of the task to mark as completed
            result: Result of the task execution
        """
        for task in plan.tasks:
            if task.id == task_id:
                task.completed = True
                task.result = result
                if task_id not in plan.completed_tasks:
                    plan.completed_tasks.append(task_id)
                break

    def mark_task_failed(self, plan: Plan, task_id: str, error: str = "") -> None:
        """
        Mark a task as failed in the plan.

        Args:
            plan: The execution plan
            task_id: ID of the task to mark as failed
            error: Error message if applicable
        """
        if task_id not in plan.failed_tasks:
            plan.failed_tasks.append(task_id)