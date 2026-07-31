from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

from agents.tool_registry import Tool


class RewriteTool(Tool):
    """
    Tool for rewriting content in different styles (simplify, summarize, expand, bullet points, etc.).
    Adapts complexity and format based on target audience and learning objectives.
    """

    name: str = "rewrite"
    description: str = "Rewrite content in different styles (simplify, summarize, expand, bullet points, etc.)"

    def __init__(self) -> None:
        super().__init__()

    def execute(
        self,
        content: str,
        style: str = "simplify",
        target_audience: str = "general",
        max_length: Optional[int] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Rewrite content according to the specified style and target audience.

        Args:
            content: The content to rewrite
            style: Rewriting style (simplify, summarize, expand, bullet_points, study_notes, flashcards, explain_like_im_5)
            target_audience: Target audience (beginner, intermediate, advanced, general, child)
            max_length: Maximum length of the output (optional)
            **kwargs: Additional arguments

        Returns:
            Dict containing the rewritten content and metadata
        """
        try:
            if not content or not content.strip():
                return {
                    "error": "empty_content",
                    "message": "No content provided to rewrite",
                    "original_content": content
                }

            # Apply the requested rewriting style
            if style == "simplify":
                rewritten = self._simplify_content(content, target_audience)
            elif style == "summarize":
                rewritten = self._summarize_content(content, target_audience, max_length)
            elif style == "expand":
                rewritten = self._expand_content(content, target_audience)
            elif style == "bullet_points":
                rewritten = self._to_bullet_points(content, target_audience)
            elif style == "study_notes":
                rewritten = self._to_study_notes(content, target_audience)
            elif style == "flashcards":
                rewritten = self._to_flashcards(content, target_audience)
            elif style == "explain_like_im_5":
                rewritten = self._explain_like_im_5(content, target_audience)
            else:
                return {
                    "error": "invalid_style",
                    "message": f"Unsupported style: {style}",
                    "supported_styles": [
                        "simplify", "summarize", "expand", "bullet_points",
                        "study_notes", "flashcards", "explain_like_im_5"
                    ]
                }

            # Apply length limit if specified
            if max_length and len(rewritten) > max_length:
                # Try to cut at a sentence boundary
                if "." in rewritten[:max_length]:
                    cutoff = rewritten.rfind(".", 0, max_length) + 1
                    rewritten = rewritten[:cutoff]
                else:
                    rewritten = rewritten[:max_length] + "..."

            return {
                "original_content": content,
                "rewritten_content": rewritten,
                "style": style,
                "target_audience": target_audience,
                "original_length": len(content),
                "rewritten_length": len(rewritten),
                "compression_ratio": len(rewritten) / len(content) if len(content) > 0 else 0,
                "message": f"Successfully rewritten content using {style} style for {target_audience} audience"
            }

        except Exception as e:
            return {
                "error": type(e).__name__,
                "message": f"Error rewriting content: {str(e)}",
                "original_content": content[:100] + "..." if len(content) > 100 else content
            }

    def _simplify_content(self, content: str, target_audience: str) -> str:
        """Simplify content for better understanding."""
        # Replace complex words with simpler alternatives
        replacements = {
            "utilize": "use",
            "facilitate": "help",
            "utilization": "use",
            "commence": "start",
            "terminate": "end",
            "subsequently": "then",
            "furthermore": "also",
            "nevertheless": "but",
            "consequently": "so",
            "additionally": "also",
            "furthermore": "also",
            "moreover": "also",
            "therefore": "so",
            "however": "but",
            "although": "though",
            "nevertheless": "but",
            "nonetheless": "but",
            "accordingly": "so",
            "as a result": "so",
            "in conclusion": "finally",
            "in summary": "basically",
            "it is important to note": "note",
            "it should be noted": "note",
            "for the purpose of": "for",
            "in order to": "to",
            "due to the fact that": "because",
            "in spite of the fact that": "although",
            "in the event that": "if",
            "at this point in time": "now",
            "prior to": "before",
            "subsequent to": "after",
            "accordance with": "per",
            "with respect to": "about",
            "in relation to": "about",
            "in accordance with": "following",
            "on the basis of": "based on",
            "in the case of": "for",
            "in the process of": "during",
            "make an attempt": "try",
            "give consideration to": "consider",
            "take into consideration": "consider",
            "have the ability to": "can",
            "is able to": "can",
            "is responsible for": "handles",
            "is required to": "must",
            "is expected to": "should",
            "is necessary to": "need to",
            "is possible to": "can",
            "is unable to": "can't",
            "is not able to": "can't"
        }

        simplified = content
        for complex_word, simple_word in replacements.items():
            # Case-insensitive replacement
            pattern = re.compile(re.escape(complex_word), re.IGNORECASE)
            simplified = pattern.sub(simple_word, simplified)

        # Break up long sentences
        sentences = re.split(r'(?<=[.!?])\s+', simplified)
        simplified_sentences = []
        for sentence in sentences:
            if len(sentence) > 200 and target_audience in ["beginner", "child"]:
                # Try to split long sentences for beginners
                parts = re.split(r'(,|\sand\s|\sbut\s|\sor\s)', sentence)
                # Simple rejoining - in reality, we'd be more sophisticated
                simplified_sentences.append(sentence)  # Keep as is for now
            else:
                simplified_sentences.append(sentence)

        simplified = ' '.join(simplified_sentences)

        # Add explanations for technical terms if audience is beginner or child
        if target_audience in ["beginner", "child"]:
            # Add simple explanations in parentheses for some technical terms
            # This is a simplified version - a real implementation would be more sophisticated
            pass

        return stripped

    def _summarize_content(self, content: str, target_audience: str, max_length: Optional[int]) -> str:
        """Create a summary of the content."""
        # Simple extractive summarization - in reality, we'd use more sophisticated NLP
        sentences = re.split(r'(?<=[.!?])\s+', content)

        if len(sentences) <= 3:
            # If there are few sentences, return most of them
            summary = ' '.join(sentences[:max(1, len(sentences) - 1)])
        else:
            # Take first, middle, and last sentences for a basic summary
            # In a real implementation, we'd score sentences by importance
            if len(sentences) >= 3:
                summary = f"{sentences[0]} {sentences[len(sentences)//2]} {sentences[-1]}"
            else:
                summary = ' '.join(sentences)

        # Apply length constraint if specified
        if max_length and len(summary) > max_length:
            # Try to cut at sentence boundary
            if "." in summary[:max_length]:
                cutoff = summary.rfind(".", 0, max_length) + 1
                summary = summary[:cutoff]
            else:
                summary = summary[:max_length] + "..."

        return summary

    def _expand_content(self, content: str, target_audience: str) -> str:
        """Expand content with additional explanations and examples."""
        expanded = content

        # Add elaboration based on target audience
        if target_audience == "beginner":
            expanded += "\n\n💡 **Note for beginners:** This concept might seem challenging at first. Take your time to understand each part, and don't hesitate to ask for clarification or examples."
        elif target_audience == "advanced":
            expanded += "\n\n🔍 **For advanced learners:** Consider how this concept relates to more complex topics or real-world applications in your field of interest."

        # Add a simple example placeholder (in reality, we'd generate relevant examples)
        if "definition" in content.lower() or "is" in content.lower()[:50]:
            expanded += "\n\n📝 **Example:** [A relevant example would be inserted here based on the specific content]"

        return expanded

    def _to_bullet_points(self, content: str, target_audience: str) -> str:
        """Convert content to bullet point format."""
        # Split into sentences or logical sections
        sentences = re.split(r'(?<=[.!?])\s+', content)

        # Filter out empty sentences
        sentences = [s.strip() for s in sentences if s.strip()]

        # Convert to bullet points
        bullet_points = []
        for sentence in sentences:
            # Clean up the sentence for bullet point
            clean_sentence = sentence.strip()
            if not clean_sentence.endswith(('.', '!', '?')):
                clean_sentence += '.'
            bullet_points.append(f"• {clean_sentence}")

        result = '\n'.join(bullet_points)

        # Add header based on audience
        if target_audience == "beginner":
            result = "📝 **Key Points to Remember:**\n\n" + result
        elif target_audience == "advanced":
            result = "🔑 **Main Concepts:**\n\n" + result
        else:
            result = "📋 **Summary:**\n\n" + result

        return result

    def _to_study_notes(self, content: str, target_audience: str) -> str:
        """Convert content to study notes format."""
        # Start with a title
        lines = ["# Study Notes\n"]

        # Add the content with some formatting
        lines.append("## Overview\n")
        lines.append(content)
        lines.append("\n")

        # Add key concepts section (simplified)
        lines.append("## Key Concepts\n")
        # Extract potential key concepts (simplified)
        words = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', content)
        unique_words = list(set(words))[:5]  # Top 5 unique capitalized phrases
        if unique_words:
            for word in unique_words:
                lines.append(f"- {word}")
        else:
            lines.append("- [Key concepts would be extracted here]")
        lines.append("\n")

        # Add summary
        lines.append("## Summary\n")
        sentences = re.split(r'(?<=[.!?])\s+', content)
        if len(sentences) >= 3:
            summary = f"{sentences[0]} {sentences[len(sentences)//2]}"
        else:
            summary = ' '.join(sentences)
        lines.append(f"{summary}.\n")

        # Add study tips based on audience
        if target_audience == "beginner":
            lines.append("## 📚 Study Tips\n")
            lines.append("- Take breaks every 25-30 minutes\n")
            lines.append("- Explain concepts out loud to yourself\n")
            lines.append("- Create examples related to your experience\n")
        elif target_audience == "advanced":
            lines.append("## 🔍 Advanced Exploration\n")
            lines.append("- How does this connect to other topics you've learned?\n")
            lines.append("- What are the limitations or edge cases of this concept?\n")
            lines.append("- Can you think of real-world applications?\n")
        else:
            lines.append("## 💡 Study Suggestions\n")
            lines.append("- Review these notes after 24 hours\n")
            lines.append("- Try to explain the main idea in your own words\n")
            lines.append("- Create one practice question based on this material\n")

        return ''.join(lines)

    def _to_flashcards(self, content: str, target_audience: str) -> str:
        """Convert content to flashcard format."""
        lines = ["# Flashcards\n"]

        # Extract potential question-answer pairs (simplified approach)
        sentences = re.split(r'(?<=[.!?])\s+', content)

        # Look for patterns that suggest definitions or explanations
        flashcards = []
        for i, sentence in enumerate(sentences):
            sentence = sentence.strip()
            if not sentence:
                continue

            # Simple heuristic: if sentence contains "is" or "are" and is not too long,
            # it might be a definition suitable for a flashcard
            if len(sentence) < 200 and (' is ' in sentence.lower() or ' are ' in sentence.lower()):
                # Create a flashcard: question = concept, answer = explanation
                parts = sentence.split(' is ', 1) if ' is ' in sentence else sentence.split(' are ', 1)
                if len(parts) == 2:
                    concept = parts[0].strip()
                    explanation = parts[1].strip()
                    if not explanation.endswith('.'):
                        explanation += '.'
                    flashcards.append(f"Q: What is {concept}?\nA: {explanation}\n")

            # Alternative: treat every few sentences as a flashcard
            elif i % 3 == 0 and len(sentences) > i + 2:
                question = f"Explain the concept discussed in sentence {i+1}."
                answer = f"{sentences[i]} {sentences[i+1] if i+1 < len(sentences) else ''} {sentences[i+2] if i+2 < len(sentences) else ''}".strip()
                if not answer.endswith('.'):
                    answer += '.'
                flashcards.append(f"Q: {question}\nA: {answer}\n")

        # If we didn't create enough flashcards, create some generic ones
        if len(flashcards) < 2:
            # Create flashcards from sentence chunks
            for i in range(0, min(len(sentences), 6), 2):
                if i + 1 < len(sentences):
                    q = f"What is a key point about the topic discussed?"
                    a = f"{sentences[i].strip()} {sentences[i+1].strip()}"
                    if not a.endswith('.'):
                        a += '.'
                    flashcards.append(f"Q: {q}\nA: {a}\n")

        # Limit to reasonable number of flashcards
        flashcards = flashcards[:10]

        # Add header based on audience
        if target_audience == "beginner":
            lines.append("🎓 **Beginner Flashcards - Focus on Basics**\n\n")
        elif target_audience == "advanced":
            lines.append("🧠 **Advanced Flashcards - Deep Understanding**\n\n")
        else:
            lines.append("📚 **Study Flashcards**\n\n")

        lines.extend(flashcards)

        # Add study tips
        lines.append("\n## 📖 How to Use These Flashcards\n")
        lines.append("1. Read the question and try to answer it out loud\n")
        lines.append("2. Check your answer by looking at the back\n")
        lines.append("3. If correct, place in the 'known' pile; if wrong, place in 'to review' pile\n")
        lines.append("4. Review the 'to review' pile more frequently\n")
        lines.append("5. Shuffle the deck regularly to avoid memorizing order\n")

        return ''.join(lines)

    def _explain_like_im_5(self, content: str, target_audience: str) -> str:
        """Explain the concept as if talking to a 5-year-old."""
        # This is a simplified implementation - a real version would use more sophisticated techniques
        explained = "Imagine you're explaining this to a 5-year-old:\n\n"

        # Replace complex words with very simple ones
        simple_replacements = {
            "because": "because",
            "but": "but",
            "and": "and",
            "or": "or",
            "if": "if",
            "then": "then",
            "when": "when",
            "where": "where",
            "what": "what",
            "how": "how",
            "why": "why",
            "yes": "yes",
            "no": "no",
            "is": "is",
            "are": "are",
            "was": "was",
            "were": "were",
            "have": "have",
            "has": "has",
            "had": "had",
            "do": "do",
            "does": "does",
            "did": "did",
            "can": "can",
            "will": "will",
            "would": "would",
            "should": "should",
            "could": "could",
            "this": "this",
            "that": "that",
            "these": "these",
            "those": "those",
            "my": "my",
            "your": "your",
            "our": "our",
            "it": "it",
            "he": "he",
            "she": "she",
            "they": "they",
            "we": "we",
            "me": "me",
            "him": "him",
            "her": "her",
            "us": "us",
            "them": "them"
        }

        # For a 5-year-old explanation, we'd want to use concrete examples, analogies, and simple words
        # This is a placeholder implementation
        explained += "This is like when you [simple analogy]. When you [action], it [result]. "
        explained += "Remember: [simple summary]. Isn't that cool? 😊"

        # Add engaging elements for children
        if target_audience == "child":
            explained += "\n\n🎨 **Try this:** Draw a picture of what you just learned!\n"
            explained += "❓ **Question:** What part was your favorite? Why?"

        return stripped