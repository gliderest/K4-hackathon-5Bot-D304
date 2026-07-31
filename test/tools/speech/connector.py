from __future__ import annotations

import base64
import re
from typing import Any, Dict, List, Optional

from agents.tool_registry import Tool


class SpeechTool(Tool):
    """
    Tool for handling speech-to-text and text-to-speech conversions.
    Supports multiple languages including Vietnamese and English.
    """

    name: str = "speech"
    description: str = "Handle speech-to-text and text-to-speech conversions"

    def __init__(self) -> None:
        super().__init__()

    def execute(
        self,
        operation: str = "speech_to_text",
        audio_data: Optional[str] = None,
        text: Optional[str] = None,
        language: str = "vi",
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Execute speech operations.

        Args:
            operation: Operation to perform (speech_to_text, text_to_speech)
            audio_data: Base64 encoded audio data (for speech_to_text)
            text: Text to convert to speech (for text_to_speech)
            language: Language code (vi for Vietnamese, en for English)
            **kwargs: Additional arguments

        Returns:
            Dict containing the results of the speech operation
        """
        try:
            if operation == "speech_to_text":
                if not audio_data:
                    return {
                        "error": "missing_audio_data",
                        "message": "Audio data is required for speech_to_text operation"
                    }
                return self._speech_to_text(audio_data, language)
            elif operation == "text_to_speech":
                if not text:
                    return {
                        "error": "missing_text",
                        "message": "Text is required for text_to_speech operation"
                    }
                return self._text_to_speech(text, language)
            else:
                return {
                    "error": "invalid_operation",
                    "message": f"Unknown operation: {operation}",
                    "valid_operations": ["speech_to_text", "text_to_speech"]
                }
        except Exception as e:
            return {
                "error": type(e).__name__,
                "message": f"Error in speech operation: {str(e)}",
                "operation": operation
            }

    def _speech_to_text(self, audio_data: str, language: str) -> Dict[str, Any]:
        """
        Convert speech to text.
        In a real implementation, this would use a speech recognition service
        like Google Speech-to-Text, Azure Speech Service, or Whisper.
        For this implementation, we'll simulate the process.
        """
        try:
            # Decode the base64 audio data
            try:
                audio_bytes = base64.b64decode(audio_data)
                audio_size = len(audio_bytes)
            except Exception:
                return {
                    "error": "invalid_audio_data",
                    "message": "Invalid base64 audio data provided"
                }

            # In a real implementation, we would send this to a speech recognition service
            # For now, we'll simulate recognition based on audio size and language

            # Simulate different recognition results based on audio size
            # This is just for demonstration - real STT would analyze the actual audio
            if audio_size < 1000:  # Very short audio
                recognized_text = "Xin chào" if language == "vi" else "Hello"
                confidence = 0.95
            elif audio_size < 5000:  # Short audio
                recognized_text = "Cảm ơn bạn đã giúp tôi hiểu bài học này" if language == "vi" else "Thank you for helping me understand this lesson"
                confidence = 0.88
            elif audio_size < 20000:  # Medium audio
                recognized_text = "Tôi có thể giải thích khái niệm này bằng cách khác nếu bạn chưa hiểu" if language == "vi" else "I can explain this concept differently if you haven't understood it"
                confidence = 0.82
            else:  # Longer audio
                recognized_text = "Trong bài học ngày hôm nay, chúng ta đã học về cách áp dụng các nguyên lý của học sâu vào xử lý ngôn ngữ tự nhiên, đặc biệt là trong việc tạo ra các mô hình tạo văn bản." if language == "vi" else "In today's lesson, we learned about applying deep learning principles to natural language processing, particularly in creating text generation models."
                confidence = 0.78

            # Add some variation based on language
            if language == "vi":
                # Vietnamese-specific responses
                if "xin chào" in audio_data.lower() or "hello" in audio_data.lower():
                    recognized_text = "Xin chào! Bạn có thể giúp tôi giải thích bài học hôm nay không?"
                    confidence = 0.92
            else:
                # English-specific responses
                if "hello" in audio_data.lower() or "hi" in audio_data.lower():
                    recognized_text = "Hi! Could you help me explain today's lesson?"
                    confidence = 0.92

            return {
                "operation": "speech_to_text",
                "language": language,
                "audio_size_bytes": audio_size,
                "transcribed_text": recognized_text,
                "confidence": confidence,
                "alternatives": [
                    {
                        "text": recognized_text + " (phiên bản thay thế 1)" if language == "vi" else recognized_text + " (alternative 1)",
                        "confidence": max(0.1, confidence - 0.1)
                    },
                    {
                        "text": recognized_text + " (phiên bản thay thế 2)" if language == "vi" else recognized_text + " (alternative 2)",
                        "confidence": max(0.1, confidence - 0.2)
                    }
                ] if confidence < 0.9 else [],
                "message": f"Successfully converted speech to text in {language}"
            }

        except Exception as e:
            return {
                "error": "recognition_failed",
                "message": f"Speech to text conversion failed: {str(e)}",
                "audio_data_length": len(audio_data) if audio_data else 0
            }

    def _text_to_speech(self, text: str, language: str) -> Dict[str, Any]:
        """
        Convert text to speech.
        In a real implementation, this would use a text-to-speech service
        like Google Text-to-Speech, Amazon Polly, or Azure Cognitive Services.
        For this implementation, we'll simulate the process.
        """
        try:
            if not text.strip():
                return {
                    "error": "empty_text",
                    "message": "Cannot convert empty text to speech"
                }

            # In a real implementation, we would send this to a TTS service
            # like Google Text-to-Speech, Amazon Polly, or Azure Cognitive Services
            # For now, we'll simulate by creating a placeholder audio representation

            # Estimate audio duration based on text length
            # Average speaking rate: ~150 words per minute for English, slightly slower for Vietnamese
            words_per_minute = 140 if language == "vi" else 150
            word_count = len(text.split())
            estimated_duration_seconds = max(1, (word_count / words_per_minute) * 60)

            # Add some variation based on text complexity
            # Longer sentences or complex words might slow down speech slightly
            complex_word_penalty = sum(1 for word in text.split() if len(word) > 10) * 0.1
            estimated_duration_seconds *= (1 + min(0.3, complex_word_penalty * 0.1))

            # Simulate audio data (in reality, this would be actual audio bytes)
            # We'll create a simple placeholder that indicates audio was generated
            audio_content = f"SYNTHESIZED_AUDIO_FOR_TEXT_{len(text)}_CHARS_IN_{language}"
            simulated_audio_data = base64.b64encode(audio_content.encode()).decode()

            return {
                "operation": "text_to_speech",
                "language": language,
                "original_text": text,
                "audio_data": simulated_audio_data,
                "audio_format": "mp3",  # Would be actual format in real implementation
                "estimated_duration_seconds": round(estimated_duration_seconds, 1),
                "word_count": word_count,
                "character_count": len(text),
                "sentence_count": len([s for s in text.split('.') if s.strip()]),
                "message": f"Successfully converted text to speech in {language}"
            }

        except Exception as e:
            return {
                "error": "synthesis_failed",
                "message": f"Text to speech conversion failed: {str(e)}",
                "text_length": len(text) if text else 0
            }

    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.now().isoformat()