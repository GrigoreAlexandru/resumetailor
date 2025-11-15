"""Ollama LLM provider implementation."""
import logging
from typing import List, Iterator, Any
import ollama
from .base import BaseLLMProvider, LLMMessage, LLMResponse

logger = logging.getLogger(__name__)


class OllamaProvider(BaseLLMProvider):
    """Ollama LLM provider."""

    def __init__(
        self,
        model: str = "llama3.1:8b",
        temperature: float = 0.3,
        base_url: str = "http://localhost:11434",
        **kwargs: Any
    ):
        super().__init__(model, temperature, **kwargs)
        self.client = ollama.Client(host=base_url)
        logger.info(f"Initialized Ollama provider with model: {model}")

    def chat(
        self,
        messages: List[LLMMessage],
        **kwargs: Any
    ) -> LLMResponse:
        """Send chat completion request to Ollama.

        Args:
            messages: Conversation messages
            **kwargs: Additional Ollama options (format, keep_alive, etc.)

        Returns:
            LLMResponse with generated text
        """
        # Convert messages to Ollama format
        ollama_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]

        # Merge options
        options = {
            "temperature": self.temperature,
            **self.kwargs,
            **kwargs
        }

        try:
            response = self.client.chat(
                model=self.model,
                messages=ollama_messages,
                options=options
            )

            return LLMResponse(
                content=response['message']['content'],
                model=self.model,
                usage={
                    "prompt_tokens": response.get('prompt_eval_count', 0),
                    "completion_tokens": response.get('eval_count', 0),
                },
                metadata={
                    "total_duration": response.get('total_duration'),
                    "load_duration": response.get('load_duration'),
                }
            )

        except Exception as e:
            logger.error(f"Ollama API error: {e}")
            raise RuntimeError(f"Failed to get LLM response: {e}") from e

    def stream_chat(
        self,
        messages: List[LLMMessage],
        **kwargs: Any
    ) -> Iterator[str]:
        """Stream chat completion from Ollama.

        Yields:
            Chunks of response text
        """
        ollama_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]

        options = {
            "temperature": self.temperature,
            **self.kwargs,
            **kwargs
        }

        try:
            stream = self.client.chat(
                model=self.model,
                messages=ollama_messages,
                options=options,
                stream=True
            )

            for chunk in stream:
                if 'message' in chunk and 'content' in chunk['message']:
                    yield chunk['message']['content']

        except Exception as e:
            logger.error(f"Ollama streaming error: {e}")
            raise RuntimeError(f"Failed to stream LLM response: {e}") from e
