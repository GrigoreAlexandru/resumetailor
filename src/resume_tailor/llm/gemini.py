"""Gemini LLM provider."""
import logging
import google.generativeai as genai
from typing import Any, Dict, Iterator, List, Tuple

from resume_tailor.config.settings import settings
from resume_tailor.llm.base import LLMMessage, LLMResponse, BaseLLMProvider

logger = logging.getLogger(__name__)


class GeminiLLM(BaseLLMProvider):
    """LLM provider for Google Gemini models."""

    def __init__(self, model: str, temperature: float = 0.3, **kwargs: Any):
        super().__init__(model, temperature, **kwargs)
        if not settings.gemini_api_key:
            raise ValueError("GEMINI_API_KEY is not set.")
        
        genai.configure(api_key=settings.gemini_api_key.get_secret_value())
        self.generation_config = {"temperature": self.temperature}

    def chat(self, messages: List[LLMMessage], **kwargs: Any) -> LLMResponse:
        """Send chat completion request to Gemini."""
        logger.debug(f"Gemini chat received messages: {messages}")
        system_prompt, history, last_message = self._prepare_chat(messages)
        logger.debug(f"Prepared chat. System: '{system_prompt}', History: {history}, Last Message: '{last_message}'")

        if not last_message:
            raise ValueError("Cannot send an empty message to the Gemini API.")

        # Only include system_instruction if it's not empty
        model_kwargs = {
            "model_name": self.model,
            "generation_config": self.generation_config,
        }
        if system_prompt:
            model_kwargs["system_instruction"] = system_prompt

        client = genai.GenerativeModel(**model_kwargs)

        chat_session = client.start_chat(history=history)
        response = chat_session.send_message(last_message, **kwargs)

        usage_data = self._extract_usage(response)

        return LLMResponse(
            content=response.text,
            model=self.model,
            usage=usage_data,
            metadata={"prompt_feedback": response.prompt_feedback},
        )

    def stream_chat(self, messages: List[LLMMessage], **kwargs: Any) -> Iterator[str]:
        """Stream chat completion from Gemini."""
        logger.debug(f"Gemini stream_chat received messages: {messages}")
        system_prompt, history, last_message = self._prepare_chat(messages)
        logger.debug(f"Prepared stream_chat. System: '{system_prompt}', History: {history}, Last Message: '{last_message}'")

        if not last_message:
            raise ValueError("Cannot send an empty message to the Gemini API.")

        # Only include system_instruction if it's not empty
        model_kwargs = {
            "model_name": self.model,
            "generation_config": self.generation_config,
        }
        if system_prompt:
            model_kwargs["system_instruction"] = system_prompt

        client = genai.GenerativeModel(**model_kwargs)

        chat_session = client.start_chat(history=history)
        response_stream = chat_session.send_message(
            last_message, stream=True, **kwargs
        )

        for chunk in response_stream:
            if chunk.text:
                yield chunk.text

    def _prepare_chat(self, messages: List[LLMMessage]) -> Tuple[str, List[Dict[str, Any]], str]:
        """Prepare messages for a Gemini chat session."""
        system_prompt = ""
        history = []

        # Extract system prompt
        if messages and messages[0].role == "system":
            system_prompt = messages[0].content
            messages = messages[1:]

        # Convert history, mapping 'assistant' to 'model'
        if len(messages) > 1:
            for msg in messages[:-1]:
                role = "model" if msg.role == "assistant" else msg.role
                history.append({"role": role, "parts": [msg.content]})
        
        # Get the last message
        last_message = messages[-1].content if messages else ""

        return system_prompt, history, last_message

    def _extract_usage(self, response: Any) -> Dict[str, int]:
        """Extract token usage data from the response if available."""
        usage_data = {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
        }
        if hasattr(response, 'usage_metadata'):
            usage_data["prompt_tokens"] = response.usage_metadata.prompt_token_count
            usage_data["completion_tokens"] = response.usage_metadata.candidates_token_count
            usage_data["total_tokens"] = response.usage_metadata.total_token_count
        return usage_data
