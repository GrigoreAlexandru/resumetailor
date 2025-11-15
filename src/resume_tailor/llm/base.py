"""Abstract base class for LLM providers."""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List, Iterator
from pydantic import BaseModel


class LLMMessage(BaseModel):
    """Single message in conversation."""
    role: str  # system, user, assistant
    content: str


class LLMResponse(BaseModel):
    """Standardized LLM response."""
    content: str
    model: str
    usage: Optional[Dict[str, int]] = None  # tokens used
    metadata: Dict[str, Any] = {}


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers."""

    def __init__(self, model: str, temperature: float = 0.3, **kwargs: Any):
        self.model = model
        self.temperature = temperature
        self.kwargs = kwargs

    @abstractmethod
    def chat(
        self,
        messages: List[LLMMessage],
        **kwargs: Any
    ) -> LLMResponse:
        """Send chat completion request.

        Args:
            messages: Conversation history
            **kwargs: Provider-specific options

        Returns:
            Standardized response
        """
        pass

    @abstractmethod
    def stream_chat(
        self,
        messages: List[LLMMessage],
        **kwargs: Any
    ) -> Iterator[str]:
        """Stream chat completion.

        Yields chunks of response text.
        """
        pass

    def simple_completion(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Convenience method for single prompt completion.

        Args:
            prompt: User prompt
            system_prompt: Optional system instruction

        Returns:
            Response text
        """
        messages = []
        if system_prompt:
            messages.append(LLMMessage(role="system", content=system_prompt))
        messages.append(LLMMessage(role="user", content=prompt))

        response = self.chat(messages)
        return response.content
