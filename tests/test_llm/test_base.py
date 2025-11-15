"""Tests for LLM base classes."""
import pytest
from resume_tailor.llm.base import LLMMessage, LLMResponse


def test_llm_message_creation() -> None:
    """Test creating LLM message."""
    msg = LLMMessage(role="user", content="Hello")

    assert msg.role == "user"
    assert msg.content == "Hello"


def test_llm_response_creation() -> None:
    """Test creating LLM response."""
    response = LLMResponse(
        content="Hello back",
        model="test-model",
        usage={"prompt_tokens": 10, "completion_tokens": 5}
    )

    assert response.content == "Hello back"
    assert response.model == "test-model"
    assert response.usage is not None
    assert response.usage["prompt_tokens"] == 10
