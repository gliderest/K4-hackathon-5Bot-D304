from __future__ import annotations

import random
from typing import Any, Dict, List, Optional

from agents.tool_registry import Tool


class QuizTool(Tool):
    """
    Tool for generating quiz questions based on learning state and topic.
    Supports multiple question types and adapts difficulty based on student performance.
    """

    name: str = "quiz"
    description: str = "Generate quiz questions based on learning state and topic"

    def __init__(self) -> None:
        super().__init__()

    def execute(
        self,
        topic: str,
        question_type: str = "mixed",
        difficulty: str = "adaptive",
        count: int = 5,
        learning_state: Optional[Dict[str, Any]] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Generate quiz questions for the specified topic.

        Args:
            topic: The topic to generate questions about
            question_type: Type of questions (multiple_choice, true_false, short_answer, mixed)
            difficulty: Difficulty level (easy, medium, hard, adaptive)
            count: Number of questions to generate
            learning_state: Optional learning state data to adapt question difficulty
            **kwargs: Additional arguments

        Returns:
            Dict containing the generated questions and metadata
        """
        try:
            if not topic or not topic.strip():
                return {
                    "error": "empty_topic",
                    "message": "No topic provided for quiz generation",
                    "questions": []
                }

            # Determine actual difficulty if adaptive
            actual_difficulty = difficulty
            if difficulty == "adaptive" and learning_state:
                actual_difficulty = self._determine_adaptive_difficulty(topic, learning_state)
            elif difficulty == "adaptive":
                # Default to medium if no learning state provided
                actual_difficulty = "medium"

            # Generate questions based on type
            questions = []
            if question_type == "multiple_choice":
                questions = self._generate_multiple_choice(topic, count, actual_difficulty)
            elif question_type == "true_false":
                questions = self._generate_true_false(topic, count, actual_difficulty)
            elif question_type == "short_answer":
                questions = self._generate_short_answer(topic, count, actual_difficulty)
            elif question_type == "mixed":
                questions = self._generate_mixed_questions(topic, count, actual_difficulty)
            else:
                return {
                    "error": "invalid_question_type",
                    "message": f"Unsupported question type: {question_type}",
                    "supported_types": ["multiple_choice", "true_false", "short_answer", "mixed"]
                }

            return {
                "topic": topic,
                "questions": questions,
                "question_count": len(questions),
                "question_type": question_type,
                "difficulty": actual_difficulty,
                "generated_at": self._get_timestamp(),
                "message": f"Generated {len(questions)} {question_type} questions on {topic} at {actual_difficulty} difficulty"
            }

        except Exception as e:
            return {
                "error": type(e).__name__,
                "message": f"Error generating quiz: {str(e)}",
                "topic": topic
            }

    def _determine_adaptive_difficulty(self, topic: str, learning_state: Dict[str, Any]) -> str:
        """Determine appropriate difficulty based on learning state."""
        mastery_score = learning_state.get("mastery_scores", {}).get(topic, 0.5)

        if mastery_score >= 0.8:
            return "hard"  # Challenge advanced learners
        elif mastery_score >= 0.6:
            return "medium"  # Intermediate level
        else:
            return "easy"  # Build foundational understanding

    def _generate_multiple_choice(self, topic: str, count: int, difficulty: str) -> List[Dict[str, Any]]:
        """Generate multiple choice questions."""
        questions = []

        # Question templates based on difficulty
        if difficulty == "easy":
            templates = [
                {
                    "question": f"What is the primary purpose of {topic}?",
                    "options": [
                        f"To understand {topic} basics",
                        f"To master advanced {topic} applications",
                        f"To forget {topic} completely",
                        f"To avoid learning about {topic}"
                    ],
                    "correct": 0,
                    "explanation": f"The primary purpose of {topic} is to understand its basics."
                },
                {
                    "question": f"Which of the following best describes {topic}?",
                    "options": [
                        f"A fundamental concept in the subject area",
                        f"An unrelated topic about cooking",
                        f"A type of musical instrument",
                        f"A historical event from the 1800s"
                    ],
                    "correct": 0,
                    "explanation": f"{topic} is a fundamental concept in the subject area."
                }
            ]
        elif difficulty == "medium":
            templates = [
                {
                    "question": f"How does {topic} relate to other concepts in the field?",
                    "options": [
                        f"It builds upon foundational principles",
                        f"It contradicts all previous knowledge",
                        f"It has no relationship to other topics",
                        f"It replaces all other concepts entirely"
                    ],
                    "correct": 0,
                    "explanation": f"{topic} builds upon foundational principles in the field."
                },
                {
                    "question": f"What is a common application of {topic}?",
                    "options": [
                        f"Solving practical problems in the domain",
                        f"Creating artistic masterpieces",
                        f"Predicting weather patterns",
                        f"Designing fashion clothing"
                    ],
                    "correct": 0,
                    "explanation": f"A common application of {topic} is solving practical problems in the domain."
                }
            ]
        else:  # hard
            templates = [
                {
                    "question": f"What is a limitation or critique of {topic}?",
                    "options": [
                        f"It may not apply in all contexts",
                        f"It is universally perfect with no drawbacks",
                        f"It only works in laboratory settings",
                        f"It has been proven incorrect by all research"
                    ],
                    "correct": 0,
                    "explanation": f"While valuable, {topic} may not apply in all contexts and has certain limitations."
                },
                {
                    "question": f"How would you explain {topic} to someone with no background in the subject?",
                    "options": [
                        f"Using simple analogies and everyday examples",
                        f"Using advanced mathematical proofs only",
                        f"By assuming they already know the basics",
                        f"By using only technical jargon"
                    ],
                    "correct": 0,
                    "explanation": f"The best approach is using simple analogies and everyday examples."
                }
            ]

        # Generate questions by selecting and varying templates
        for i in range(count):
            template = random.choice(templates)
            question = template.copy()
            question["id"] = f"mcq_{topic}_{i+1}"
            question["type"] = "multiple_choice"
            questions.append(question)

        return questions

    def _generate_true_false(self, topic: str, count: int, difficulty: str) -> List[Dict[str, Any]]:
        """Generate true/false questions."""
        questions = []

        # Statement templates based on difficulty
        if difficulty == "easy":
            templates = [
                {
                    "statement": f"{topic} is an important concept to learn.",
                    "correct": True,
                    "explanation": f"Yes, {topic} is indeed an important concept in the field."
                },
                {
                    "statement": f"Learning {topic} has no practical applications.",
                    "correct": False,
                    "explanation": f"No, {topic} has many practical applications in real-world scenarios."
                }
            ]
        elif difficulty == "medium":
            templates = [
                {
                    "statement": f"{topic} builds directly upon foundational concepts learned earlier.",
                    "correct": True,
                    "explanation": f"Yes, {topic} typically builds upon previously learned foundational knowledge."
                },
                {
                    "statement": f"Experts in the field rarely use {topic} in their work.",
                    "correct": False,
                    "explanation": f"No, {topic} is regularly used by professionals in the field."
                }
            ]
        else:  # hard
            templates = [
                {
                    "statement": f"{topic} has remained unchanged since its initial conception.",
                    "correct": False,
                    "explanation": f"No, like most concepts, {topic} has evolved and been refined over time."
                },
                {
                    "statement": f"Understanding {topic} requires knowledge of related prerequisite topics.",
                    "correct": True,
                    "explanation": f"Yes, to fully grasp {topic}, understanding certain prerequisite topics is usually necessary."
                }
            ]

        # Generate questions by selecting and varying templates
        for i in range(count):
            template = random.choice(templates)
            question = template.copy()
            question["id"] = f"tf_{topic}_{i+1}"
            question["type"] = "true_false"
            questions.append(question)

        return questions

    def _generate_short_answer(self, topic: str, count: int, difficulty: str) -> List[Dict[str, Any]]:
        """Generate short answer questions."""
        questions = []

        # Prompt templates based on difficulty
        if difficulty == "easy":
            prompts = [
                f"Define {topic} in your own words.",
                f"Give one example of where {topic} might be used.",
                f"Why is {topic} important to learn?",
                f"What is the most basic aspect of {topic}?"
            ]
        elif difficulty == "medium":
            prompts = [
                f"Explain how {topic} relates to [another concept in the field].",
                f"What are two key characteristics of {topic}?",
                f"Describe a scenario where {topic} would be applied.",
                f"What problem does {topic} help solve?"
            ]
        else:  # hard
            prompts = [
                f"Compare and contrast {topic} with a related concept.",
                f"What are the limitations or drawbacks of {topic}?",
                f"How might {topic} evolve in the future based on current trends?",
                f"Design a simple experiment or application that demonstrates {topic}."
            ]

        # Generate questions by selecting and varying prompts
        for i in range(count):
            prompt = random.choice(prompts)
            # Replace placeholder if present
            if "[another concept in the field]" in prompt:
                prompt = prompt.replace("[another concept in the field]", f"a related concept")
            question = {
                "id": f"sa_{topic}_{i+1}",
                "type": "short_answer",
                "question": prompt,
                "sample_answer": f"[A thoughtful response would discuss key aspects of {topic}]",
                "explanation": f"This question tests understanding of {topic} at a {difficulty} level."
            }
            questions.append(question)

        return questions

    def _generate_mixed_questions(self, topic: str, count: int, difficulty: str) -> List[Dict[str, Any]]:
        """Generate a mix of question types."""
        questions = []
        question_types = ["multiple_choice", "true_false", "short_answer"]

        for i in range(count):
            q_type = random.choice(question_types)
            if q_type == "multiple_choice":
                mcqs = self._generate_multiple_choice(topic, 1, difficulty)
                questions.extend(mcqs)
            elif q_type == "true_false":
                tfs = self._generate_true_false(topic, 1, difficulty)
                questions.extend(tfs)
            else:  # short_answer
                sas = self._generate_short_answer(topic, 1, difficulty)
                questions.extend(sas)

        return questions

    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.now().isoformat()