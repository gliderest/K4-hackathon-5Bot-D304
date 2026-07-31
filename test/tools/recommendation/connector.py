from __future__ import annotations

from typing import Any, Dict, List, Optional

from agents.tool_registry import Tool


class RecommendationTool(Tool):
    """
    Tool for generating learning recommendations based on student progress.
    Suggests prerequisites, next topics, related concepts, and review plans.
    """

    name: str = "recommendation"
    description: str = "Generate learning recommendations based on student progress"

    def __init__(self) -> None:
        super().__init__()

    def execute(
        self,
        student_id: str,
        recommendation_type: str = "next_topic",
        current_topic: str = "",
        learning_state: Optional[Dict[str, Any]] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Generate learning recommendations for a student.

        Args:
            student_id: Unique identifier for the student
            recommendation_type: Type of recommendation (prerequisite, next_topic, related_concept, review_plan, alternative_explanation)
            current_topic: Current topic the student is studying
            learning_state: Optional learning state data to inform recommendations
            **kwargs: Additional arguments

        Returns:
            Dict containing recommendations and metadata
        """
        try:
            if not student_id:
                return {
                    "error": "missing_student_id",
                    "message": "Student ID is required for recommendations"
                }

            # Use provided learning state or create a basic one if not provided
            if learning_state is None:
                learning_state = {"student_id": student_id}

            # Generate recommendation based on type
            if recommendation_type == "prerequisite":
                result = self._recommend_prerequisites(current_topic, learning_state)
            elif recommendation_type == "next_topic":
                result = self._recommend_next_topic(current_topic, learning_state)
            elif recommendation_type == "related_concept":
                result = self._recommend_related_concepts(current_topic, learning_state)
            elif recommendation_type == "review_plan":
                result = self._create_review_plan(student_id, learning_state)
            elif recommendation_type == "alternative_explanation":
                result = self._suggest_alternative_explanation(current_topic, learning_state)
            else:
                return {
                    "error": "invalid_recommendation_type",
                    "message": f"Unknown recommendation type: {recommendation_type}",
                    "valid_types": ["prerequisite", "next_topic", "related_concept", "review_plan", "alternative_explanation"]
                }

            result.update({
                "student_id": student_id,
                "recommendation_type": recommendation_type,
                "generated_at": self._get_timestamp()
            })

            return result

        except Exception as e:
            return {
                "error": type(e).__name__,
                "message": f"Error generating recommendations: {str(e)}",
                "student_id": student_id,
                "recommendation_type": recommendation_type
            }

    def _recommend_prerequisites(self, topic: str, learning_state: Dict[str, Any]) -> Dict[str, Any]:
        """Recommend prerequisite knowledge for a topic."""
        # In a real implementation, this would use a curriculum map or prerequisite graph
        # For now, we'll provide some common prerequisites based on topic patterns

        prerequisites = []

        # Topic-specific prerequisites (examples)
        topic_lower = topic.lower()
        if "calculus" in topic_lower or "derivative" in topic_lower or "integral" in topic_lower:
            prerequisites = [
                "Algebra",
                "Trigonometry",
                "Functions and Graphs",
                "Limits"
            ]
        elif "statistics" in topic_lower or "probability" in topic_lower:
            prerequisites = [
                "Basic Algebra",
                "Percentages and Fractions",
                "Basic Set Theory"
            ]
        elif "programming" in topic_lower or "algorithm" in topic_lower:
            prerequisites = [
                "Logical Thinking",
                "Basic Mathematics",
                "Problem Solving Skills"
            ]
        elif "physics" in topic_lower:
            prerequisites = [
                "Algebra",
                "Trigonometry",
                "Basic Scientific Method"
            ]
        else:
            # Generic prerequisites
            prerequisites = [
                "Foundational Concepts",
                "Basic Terminology",
                "Prerequisite Skills"
            ]

        # Check learning state to see what they've already mastered
        mastery_scores = learning_state.get("mastery_scores", {})
        completed_lessons = learning_state.get("completed_lessons", [])

        # Filter out prerequisites they've already mastered
        remaining_prereqs = []
        for prereq in prerequisites:
            # Check if they've mastered it (score >= 0.8) or completed related lessons
            is_mastered = mastery_scores.get(prereq, 0) >= 0.8
            is_completed = any(prereq.lower() in lesson.lower() for lesson in completed_lessons)

            if not (is_mastered or is_completed):
                remaining_prereqs.append(prereq)

        if not remaining_prereqs:
            message = f"You appear to have the necessary prerequisites for {topic}!"
            prerequisites_to_show = []
        else:
            message = f"To succeed in {topic}, consider reviewing these prerequisite topics first:"
            prerequisites_to_show = remaining_prereqs[:3]  # Limit to top 3

        return {
            "recommendations": [{
                "type": "prerequisite",
                "topic": topic,
                "prerequisites": prerequisites_to_show,
                "message": message,
                "suggested_action": f"Review the prerequisite topics before diving deeper into {topic}",
                "priority": "high" if prerequisites_to_show else "low"
            }]
        }

    def _recommend_next_topic(self, current_topic: str, learning_state: Dict[str, Any]) -> Dict[str, Any]:
        """Recommend what to study next after mastering the current topic."""
        # In a real implementation, this would use a learning path or curriculum map

        # Get mastery level of current topic
        mastery_scores = learning_state.get("mastery_scores", {})
        current_mastery = mastery_scores.get(current_topic, 0.0)

        # Define common learning paths (simplified)
        next_topics = {
            "algebra": ["geometry", "trigonometry", "precalculus"],
            "geometry": ["trigonometry", "algebra II"],
            "trigonometry": ["precalculus", "calculus"],
            "precalculus": ["calculus", "statistics"],
            "calculus": ["differential equations", "multivariable calculus", "linear algebra"],
            "basic programming": ["data structures", "algorithms", "object-oriented programming"],
            "object-oriented programming": ["design patterns", "software architecture", "testing"],
            "data structures": ["algorithms", "database systems", "complexity theory"],
            "algorithms": ["machine learning", "ai fundamentals", "competitive programming"],
            "mechanics": ["thermodynamics", "electromagnetism", "optics"],
            "electricity and magnetism": ["waves", "optics", "modern physics"],
            "cell biology": ["genetics", "evolution", "ecology"],
            "grammar": ["writing techniques", "literature analysis", "public speaking"]
        }

        # Find suggested next topics
        suggested = []
        current_lower = current_topic.lower()

        # Direct match
        if current_lower in next_topics:
            suggested = next_topics[current_lower]
        else:
            # Partial match
            for key, values in next_topics.items():
                if key in current_lower or current_lower in key:
                    suggested = values
                    break

        # If no match found, provide general suggestions
        if not suggested:
            suggested = ["related advanced topics", "practical applications", "related fields"]

        # Filter based on mastery - only suggest next topics if current is well understood
        if current_mastery < 0.6:
            message = f"It looks like you're still building your understanding of {current_topic}. Consider strengthening your grasp before moving on."
            suggested = []  # Don't suggest next topics yet
            priority = "medium"
        elif current_mastery < 0.8:
            message = f"You're making good progress on {current_topic}! You might want to solidify your understanding before advancing."
            suggested = suggested[:1]  # Limit suggestions
            priority = "medium"
        else:
            message = f"Great job mastering {current_topic}! Here are some suggestions for what to learn next:"
            priority = "high"

        return {
            "recommendations": [{
                "type": "next_topic",
                "current_topic": current_topic,
                "suggested_topics": suggested,
                "current_mastery": current_mastery,
                "message": message,
                "suggested_action": f"Consider exploring one of the suggested topics after reviewing {current_topic} if needed",
                "priority": priority
            }]
        }

    def _recommend_related_concepts(self, topic: str, learning_state: Dict[str, Any]) -> Dict[str, Any]:
        """Recommend concepts related to the current topic."""
        # Related concepts based on domain mapping
        related_map = {
            "calculus": ["limits", "derivatives", "integrals", "differential equations"],
            "algebra": ["equations", "functions", "graphs", "polynomials"],
            "statistics": ["probability", "data analysis", "hypothesis testing", "regression"],
            "physics": ["motion", "force", "energy", "momentum"],
            "biology": ["cells", "genetics", "evolution", "ecology"],
            "programming": ["variables", "loops", "functions", "data structures"],
            "history": ["timelines", "cause and effect", "historical figures", "cultural context"],
            "literature": ["themes", "character analysis", "plot structure", "literary devices"]
        }

        # Find related concepts
        related = []
        topic_lower = topic.lower()

        # Direct match
        if topic_lower in related_map:
            related = related_map[topic_lower]
        else:
            # Partial match
            for key, values in related_map.items():
                if key in topic_lower or topic_lower in key:
                    related = values
                    break

        # If no specific mapping, provide generic related concepts
        if not related:
            related = ["fundamental principles", "real-world applications", "historical development", "related subtopics"]

        # Check what they've already mastered
        mastery_scores = learning_state.get("mastery_scores", {})
        mastered_related = [concept for concept in related if mastery_scores.get(concept, 0) >= 0.7]
        remaining_related = [concept for concept in related if mastery_scores.get(concept, 0) < 0.7]

        if mastered_related:
            message = f"You've already mastered some aspects related to {topic}: {', '.join(mastered_related[:3])}."
        else:
            message = f"To deepen your understanding of {topic}, consider exploring these related concepts:"

        return {
            "recommendations": [{
                "type": "related_concept",
                "topic": topic,
                "related_concepts": related[:3],  # Top 3
                "mastered_related": mastered_related[:3],
                "message": message,
                "suggested_action": f"Study the related concepts to build a more comprehensive understanding of {topic}",
                "priority": "medium"
            }]
        }

    def _create_review_plan(self, student_id: str, learning_state: Dict[str, Any]) -> Dict[str, Any]:
        """Create a personalized review plan based on learning state."""
        weak_concepts = learning_state.get("weak_concepts", [])
        frequently_asked = learning_state.get("frequently_asked_concepts", [])
        quiz_history = learning_state.get("quiz_history", [])
        mastery_scores = learning_state.get("mastery_scores", {})

        # Prioritize review items
        review_items = []

        # Add weak concepts (highest priority)
        for weak in weak_concepts[:3]:  # Top 3 weakest
            review_items.append({
                "topic": weak.get("concept", ""),
                "reason": "Identified as weak area based on performance",
                "priority": "high",
                "suggested_activities": ["Review explanation", "Practice problems", "Seek clarification"]
            })

        # Add frequently asked questions they struggle with
        for faq in frequently_asked[:2]:  # Top 2 most frequent
            concept = faq.get("concept", "")
            # Only add if not already in weak concepts and mastery is below 0.8
            if concept not in [item["topic"] for item in review_items] and mastery_scores.get(concept, 0) < 0.8:
                review_items.append({
                    "topic": concept,
                    "reason": f"Frequently asked about ({faq.get('count', 0)} times)",
                    "priority": "medium",
                    "suggested_activities": ["Review key points", "Create summary notes", "Teach to someone else"]
                })

        # Add recently struggled quiz topics
        recent_quizzes = sorted(quiz_history, key=lambda x: x.get("timestamp", ""), reverse=True)[:3]
        for quiz in recent_quizzes:
            topic = quiz.get("topic", "")
            score = quiz.get("score", 0.0)
            if score < 0.7 and topic not in [item["topic"] for item in review_items]:
                review_items.append({
                    "topic": topic,
                    "reason": f"Recent quiz score: {score*100:.0f}%",
                    "priority": "medium" if score >= 0.5 else "high",
                    "suggested_activities": ["Review quiz mistakes", "Retake similar problems", "Explain concepts aloud"]
                })

        # Limit total review items
        review_items = review_items[:5]

        if not review_items:
            message = "Great job! No specific review topics identified at this time. Consider exploring advanced topics or applications."
            review_items = [{
                "topic": "Advanced applications",
                "reason": "Strong performance across recent assessments",
                "priority": "low",
                "suggested_activities": ["Explore real-world applications", "Try challenging problems", "Help others learn"]
            }]
        else:
            message = f"Based on your recent performance, here's a personalized review plan:"

        return {
            "recommendations": [{
                "type": "review_plan",
                "student_id": student_id,
                "review_items": review_items,
                "message": message,
                "suggested_action": "Follow this plan to strengthen your understanding of key concepts",
                "estimated_time_minutes": sum(15 for _ in review_items),  # 15 min per item
                "priority": "high" if any(item["priority"] == "high" for item in review_items) else "medium"
            }]
        }

    def _suggest_alternative_explanation(self, topic: str, learning_state: Dict[str, Any]) -> Dict[str, Any]:
        """Suggest alternative ways to explain a concept based on learning preferences."""
        preferred_style = learning_state.get("preferred_explanation_style", "balanced")
        learning_pace = learning_state.get("learning_pace", "moderate")

        # Different explanation styles
        explanation_styles = {
            "visual": ["diagrams", "graphs", "visual metaphors", "infographics", "animations"],
            "verbal": ["lectures", "discussions", "verbal analogies", "storytelling", "mnemonics"],
            "examples": ["worked examples", "real-world applications", "case studies", "problem-solving"],
            "balanced": ["mixed media", "varied examples", "interactive explanations", "multiple representations"]
        }

        # Get recommended styles based on preference
        recommended_styles = explanation_styles.get(preferred_style, explanation_styles["balanced"])

        # Adjust based on learning pace
        pace_modifiers = {
            "slow": ["step-by-step breakdowns", "detailed explanations", "plenty of practice time"],
            "moderate": ["standard pacing", "balanced examples and theory"],
            "fast": ["advanced applications", "challenging extensions", "concept connections"]
        }

        pace_suggestions = pace_modifiers.get(learning_pace, pace_modifiers["moderate"])

        # Specific suggestions for the topic
        specific_suggestions = []
        topic_lower = topic.lower()

        if "math" in topic_lower or "calculation" in topic_lower:
            specific_suggestions = [
                "Use visual representations like graphs or geometric interpretations",
                "Work through concrete numerical examples",
                "Connect to real-world applications like physics or economics"
            ]
        elif "programming" in topic_lower or "coding" in topic_lower:
            specific_suggestions = [
                "Show code examples with explanations",
                "Use debugging walkthroughs",
                "Create small projects to apply the concept"
            ]
        elif "science" in topic_lower:
            specific_suggestions = [
                "Use laboratory demonstrations or simulations",
                "Connect to observable phenomena",
                "Apply to real-world problems or inventions"
            ]
        else:
            specific_suggestions = [
                "Use analogies from everyday life",
                "Provide historical context or development of the idea",
                "Show how it connects to other topics you know"
            ]

        return {
            "recommendations": [{
                "type": "alternative_explanation",
                "topic": topic,
                "preferred_style": preferred_style,
                "learning_pace": learning_pace,
                "recommended_styles": recommended_styles[:3],
                "pace_suggestions": pace_suggestions[:2],
                "specific_suggestions": specific_suggestions[:2],
                "message": f"Based on your learning preferences ({preferred_style} style, {learning_pace} pace), here are alternative ways to understand {topic}:",
                "suggested_action": f"Try one of these approaches if the standard explanation of {topic} isn't clicking",
                "priority": "medium"
            }]
        }

    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.now().isoformat()