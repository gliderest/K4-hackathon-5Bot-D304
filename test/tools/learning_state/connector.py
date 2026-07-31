from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from agents.tool_registry import Tool


class LearningStateTool(Tool):
    """
    Tool for managing and querying the student's learning state and progress.
    Tracks mastery, misconceptions, learning pace, and generates personalized recommendations.
    """

    name: str = "learning_state"
    description: str = "Manage and query the student's learning state and progress"

    def __init__(self, storage_path: str = "./learning_state") -> None:
        super().__init__()
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

    def execute(
        self,
        operation: str,
        student_id: str,
        topic: Optional[str] = None,
        evidence: Optional[Dict[str, Any]] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Perform operations on the learning state.

        Args:
            operation: Operation to perform (get, update, assess, get_recommendations)
            student_id: Unique identifier for the student
            topic: Specific topic to operate on (for assessment/update)
            evidence: Evidence to update learning state with (for update operation)
            **kwargs: Additional arguments

        Returns:
            Dict containing the result of the operation
        """
        try:
            if operation == "get":
                return self._get_learning_state(student_id)
            elif operation == "update":
                if not evidence:
                    return {
                        "error": "invalid_input",
                        "message": "Evidence is required for update operation"
                    }
                return self._update_learning_state(student_id, topic, evidence)
            elif operation == "assess":
                if not topic:
                    return {
                        "error": "invalid_input",
                        "message": "Topic is required for assess operation"
                    }
                return self._assess_understanding(student_id, topic)
            elif operation == "get_recommendations":
                return self._get_recommendations(student_id)
            else:
                return {
                    "error": "invalid_operation",
                    "message": f"Unknown operation: {operation}"
                }
        except Exception as e:
            return {
                "error": type(e).__name__,
                "message": f"Error in learning state operation: {str(e)}",
                "operation": operation,
                "student_id": student_id
            }

    def _get_student_file(self, student_id: str) -> Path:
        """Get the file path for a student's learning state."""
        # Sanitize student_id for use as filename
        safe_id = "".join(c for c in student_id if c.isalnum() or c in ('-', '_')).rstrip()
        return self.storage_path / f"{safe_id}.json"

    def _load_student_state(self, student_id: str) -> Dict[str, Any]:
        """Load a student's learning state from disk."""
        student_file = self._get_student_file(student_id)
        if student_file.exists():
            try:
                with open(student_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                # If file is corrupted, return default state
                pass
        return self._get_default_state(student_id)

    def _save_student_state(self, student_id: str, state: Dict[str, Any]) -> None:
        """Save a student's learning state to disk."""
        student_file = self._get_student_file(student_id)
        try:
            with open(student_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2, ensure_ascii=False)
        except Exception as e:
            raise Exception(f"Failed to save student state: {str(e)}")

    def _get_default_state(self, student_id: str) -> Dict[str, Any]:
        """Get the default learning state for a new student."""
        from datetime import datetime
        return {
            "student_id": student_id,
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "current_lesson": None,
            "completed_lessons": [],
            "visited_lessons": [],
            "weak_concepts": [],  # List of {concept: str, evidence: str, timestamp: str}
            "strong_concepts": [],  # List of {concept: str, evidence: str, timestamp: str}
            "frequently_asked_concepts": [],  # List of {concept: str, count: int}
            "mastery_scores": {},  # Dict of concept -> score (0.0 to 1.0)
            "quiz_history": [],  # List of quiz attempts
            "learning_pace": "moderate",  # slow, moderate, fast
            "preferred_explanation_style": "balanced",  # visual, verbal, examples, balanced
            "total_study_time_minutes": 0,
            "session_count": 0
        }

    def _get_learning_state(self, student_id: str) -> Dict[str, Any]:
        """Get the current learning state for a student."""
        state = self._load_student_state(student_id)
        return {
            "operation": "get",
            "student_id": student_id,
            "learning_state": state,
            "message": f"Retrieved learning state for student {student_id}"
        }

    def _update_learning_state(
        self,
        student_id: str,
        topic: Optional[str],
        evidence: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update the learning state based on new evidence."""
        state = self._load_student_state(student_id)
        from datetime import datetime
        timestamp = datetime.now().isoformat()

        # Update last updated time
        state["last_updated"] = timestamp

        # Process different types of evidence
        evidence_type = evidence.get("type", "general")

        if evidence_type == "concept_mastery":
            # Update mastery score for a concept
            concept = evidence.get("concept")
            score = evidence.get("score", 0.5)  # Default to 0.5 if not provided
            if concept:
                current_score = state["mastery_scores"].get(concept, 0.0)
                # Use a weighted average to smooth updates
                new_score = (current_score * 0.7) + (score * 0.3)
                state["mastery_scores"][concept] = max(0.0, min(1.0, new_score))

                # Update strong/weak concepts based on threshold
                if new_score >= 0.8:
                    # Strong concept
                    if not any(c["concept"] == concept for c in state["strong_concepts"]):
                        state["strong_concepts"].append({
                            "concept": concept,
                            "evidence": evidence.get("description", ""),
                            "timestamp": timestamp
                        })
                    # Remove from weak if it was there
                    state["weak_concepts"] = [
                        c for c in state["weak_concepts"] if c["concept"] != concept
                    ]
                elif new_score <= 0.3:
                    # Weak concept
                    if not any(c["concept"] == concept for c in state["weak_concepts"]):
                        state["weak_concepts"].append({
                            "concept": concept,
                            "evidence": evidence.get("description", ""),
                            "timestamp": timestamp
                        })
                    # Remove from strong if it was there
                    state["strong_concepts"] = [
                        c for c in state["strong_concepts"] if c["concept"] != concept
                    ]

        elif evidence_type == "lesson_completion":
            # Mark a lesson as completed
            lesson = evidence.get("lesson")
            if lesson and lesson not in state["completed_lessons"]:
                state["completed_lessons"].append(lesson)
                # Also add to visited if not there
                if lesson not in state["visited_lessons"]:
                    state["visited_lessons"].append(lesson)
                # Update current lesson if this was it
                if state["current_lesson"] == lesson:
                    state["current_lesson"] = None

        elif evidence_type == "lesson_visit":
            # Mark a lesson as visited
            lesson = evidence.get("lesson")
            if lesson and lesson not in state["visited_lessons"]:
                state["visited_lessons"].append(lesson)
                # Set as current lesson if not already set
                if not state["current_lesson"]:
                    state["current_lesson"] = lesson

        elif evidence_type == "question_asked":
            # Track frequently asked concepts
            concept = evidence.get("concept")
            if concept:
                # Find existing entry or create new
                found = False
                for item in state["frequently_asked_concepts"]:
                    if item["concept"] == concept:
                        item["count"] += 1
                        found = True
                        break
                if not found:
                    state["frequently_asked_concepts"].append({
                        "concept": concept,
                        "count": 1
                    })
                # Sort by count descending
                state["frequently_asked_concepts"].sort(key=lambda x: x["count"], reverse=True)
                # Keep only top 10
                state["frequently_asked_concepts"] = state["frequently_asked_concepts"][:10]

        elif evidence_type == "quiz_result":
            # Record quiz performance
            quiz_record = {
                "timestamp": timestamp,
                "topic": evidence.get("topic", "unknown"),
                "score": evidence.get("score", 0.0),
                "question_count": evidence.get("question_count", 0),
                "correct_answers": evidence.get("correct_answers", 0),
                "details": evidence.get("details", {})
            }
            state["quiz_history"].append(quiz_record)
            # Keep only last 50 quizzes
            state["quiz_history"] = state["quiz_history"][-50:]

            # Update mastery based on quiz score
            topic = evidence.get("topic")
            if topic:
                current_score = state["mastery_scores"].get(topic, 0.0)
                quiz_score = evidence.get("score", 0.0)
                # Weighted average: 70% existing, 30% new quiz
                new_score = (current_score * 0.7) + (quiz_score * 0.3)
                state["mastery_scores"][topic] = max(0.0, min(1.0, new_score))

        elif evidence_type == "learning_style_preference":
            # Update preferred explanation style
            style = evidence.get("style")
            if style in ["visual", "verbal", "examples", "balanced"]:
                state["preferred_explanation_style"] = style

        elif evidence_type == "learning_pace":
            # Update learning pace
            pace = evidence.get("pace")
            if pace in ["slow", "moderate", "fast"]:
                state["learning_pace"] = pace

        elif evidence_type == "study_time":
            # Add to total study time
            minutes = evidence.get("minutes", 0)
            if isinstance(multiples, (int, float)) and minutes > 0:
                state["total_study_time_minutes"] += int(minutes)
                state["session_count"] += 1

        # Save updated state
        self._save_student_state(student_id, state)

        return {
            "operation": "update",
            "student_id": student_id,
            "updated_at": timestamp,
            "changes_applied": [evidence_type],
            "message": f"Updated learning state for student {student_id} with {evidence_type} evidence"
        }

    def _assess_understanding(self, student_id: str, topic: str) -> Dict[str, Any]:
        """Assess the student's understanding of a specific topic."""
        state = self._load_student_state(student_id)

        # Get mastery score for the topic
        mastery_score = state["mastery_scores"].get(topic, 0.0)

        # Determine understanding level
        if mastery_score >= 0.8:
            level = "advanced"
            description = "Excellent understanding"
        elif mastery_score >= 0.6:
            level = "intermediate"
            description = "Good understanding"
        elif mastery_score >= 0.4:
            level = "developing"
            description = "Developing understanding"
        elif mastery_score >= 0.2:
            level = "beginner"
            description = "Beginning to understand"
        else:
            level = "novice"
            description = "Limited understanding"

        # Check if it's in weak/strong concepts
        is_weak = any(c["concept"] == topic for c in state["weak_concepts"])
        is_strong = any(c["concept"] == topic for c in state["strong_concepts"])

        # Get recent quiz performance_level FirebaseAnalytics
        performance_level = "needs_improvement"
        if mastery_score >= 0.8:
            performance_level = "exceeds_expectations"
        elif mastery_score >= 0.6:
            performance_level = "meets_expectations"
        elif mastery_score >= 0.4:
            performance_level = "approaching_expectations"

        return {
            "operation": "assess",
            "student_id": student_id,
            "topic": topic,
            "mastery_score": mastery_score,
            "understanding_level": level,
            "description": description,
            "is_weak_area": is_weak,
            "is_strong_area": is_strong,
            "performance_level": performance_level,
            "recommendations": self._generate_topic_recommendations(state, topic),
            "message": f"Assessed understanding of {topic} for student {student_id}"
        }

    def _get_recommendations(self, student_id: str) -> Dict[str, Any]:
        """Generate learning recommendations based on the student's state."""
        state = self._load_student_state(student_id)

        recommendations = []

        # Recommend based on weak concepts
        weak_concepts = state["weak_concepts"]
        if weak_concepts:
            # Sort by recency (most recent first)
            weak_concepts_sorted = sorted(
                weak_concepts,
                key=lambda x: x["timestamp"],
                reverse=True
            )
            for weak_concept in weak_concepts_sorted[:3]:  # Top 3 weakest
                recommendations.append({
                    "type": "review",
                    "priority": "high",
                    "topic": weak_concept["concept"],
                    "reason": f"Recently identified as weak area",
                    "suggested_action": f"Review {weak_concept['concept']} using explanation and practice problems",
                    "resources": ["course_materials", "practice_exercises"]
                })

        # Recommend based on frequently asked questions
        frequent_questions = state["frequently_asked_concepts"]
        if frequent_questions:
            for item in frequent_questions[:2]:  # Top 2 most frequent
                recommendations.append({
                    "type": "practice",
                    "priority": "medium",
                    "topic": item["concept"],
                    "reason": f"Frequently asked about ({item['count']} times)",
                    "suggested_action": f"Practice problems and examples related to {item['concept']}",
                    "resources": ["quiz_generator", "practice_problems"]
                })

        # Recommend next topic based on completed lessons
        completed = set(state["completed_lessons"])
        # This would normally come from a course curriculum map
        # For now, we'll provide a generic recommendation
        if completed:
            recommendations.append({
                "type": "next_steps",
                "priority": "medium",
                "suggested_action": "Continue with the next lesson in your learning path",
                "resources": ["course_curriculum"]
            })

        # Recommend based on learning pace
        pace = state["learning_pace"]
        if pace == "slow":
            recommendations.append({
                "type": "pacing",
                "priority": "low",
                "suggested_action": "Consider spending more time on foundational concepts",
                "resources": ["review_materials"]
            })
        elif pace == "fast":
            recommendations.append({
                "type": "pacing",
                "priority": "low",
                "suggested_action": "You might be ready for more advanced topics",
                "resources": ["advanced_topics"]
            })

        # If no specific recommendations, give general advice
        if not recommendations:
            recommendations.append({
                "type": "general",
                "priority": "low",
                "suggested_action": "Continue with your current study plan",
                "resources": ["course_materials"]
            })

        return {
            "operation": "get_recommendations",
            "student_id": student_id,
            "recommendations": recommendations,
            "generated_at": self._get_timestamp(),
            "message": f"Generated {len(recommendations)} recommendations for student {student_id}"
        }

    def _generate_topic_recommendations(self, state: Dict[str, Any], topic: str) -> List[Dict[str, Any]]:
        """Generate specific recommendations for a topic based on learning state."""
        recommendations = []
        mastery_score = state["mastery_scores"].get(topic, 0.0)
        preferred_style = state["preferred_explanation_style"]
        learning_pace = state["learning_pace"]

        if mastery_score < 0.4:
            # Struggling with the topic
            recommendations.append({
                "type": "foundational_review",
                "priority": "high",
                "suggestion": f"Review prerequisite concepts for {topic}",
                "reason": "Low mastery score suggests foundation gaps"
            })
            recommendations.append({
                "type": "alternative_explanation",
                "priority": "high",
                "suggestion": f"Try {preferred_style} explanation of {topic}",
                "reason": f"Matches your preferred learning style ({preferred_style})"
            })
        elif mastery_score < 0.7:
            # Developing understanding
            recommendations.append({
                "type": "practice",
                "priority": "medium",
                "suggestion": f"Practice problems on {topic}",
                "reason": "Moderate mastery suggests need for application practice"
            })
            if learning_pace == "slow":
                recommendations.append({
                    "type": "breakdown",
                    "priority": "medium",
                    "suggestion": f"Break {topic} into smaller sub-concepts",
                    "reason": "Matches your learning pace preference"
                })
        else:
            # Good understanding
            recommendations.append({
                "type": "extension",
                "priority": "medium",
                "suggestion": f"Explore advanced applications of {topic}",
                "reason": "Strong mastery suggests readiness for extension"
            })
            recommendations.append({
                "type": "teaching_back",
                "priority": "low",
                "suggestion": f"Try explaining {topic} to someone else",
                "reason": "Teaching reinforces learning"
            })

        return recommendations

    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.now().isoformat()