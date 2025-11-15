"""Tests for Gemini LLM provider."""
import pytest
from unittest.mock import MagicMock, patch

from pydantic import SecretStr
from resume_tailor.config.settings import settings, LLMProvider
from resume_tailor.llm.gemini import GeminiLLM
from resume_tailor.llm.base import LLMMessage


@pytest.fixture
def mock_gemini_client(mocker):
    """Fixture to mock the google.generativeai client."""
    mock_configure = mocker.patch("google.generativeai.configure")
    
    mock_response = MagicMock()
    mock_response.text = "This is a Gemini response."
    mock_response.usage_metadata = MagicMock()
    mock_response.usage_metadata.prompt_token_count = 10
    mock_response.usage_metadata.candidates_token_count = 20
    mock_response.usage_metadata.total_token_count = 30

    mock_chat_session = MagicMock()
    mock_chat_session.send_message.return_value = mock_response

    mock_model_instance = MagicMock()
    mock_model_instance.start_chat.return_value = mock_chat_session

    mock_generative_model_class = mocker.patch(
        "google.generativeai.GenerativeModel", return_value=mock_model_instance
    )
    
    return {
        "configure": mock_configure,
        "model_class": mock_generative_model_class,
        "model_instance": mock_model_instance,
        "chat_session": mock_chat_session,
    }


def test_gemini_llm_chat(mock_gemini_client):
    """Test the chat method of the GeminiLLM provider."""
    # Arrange
    settings.llm_provider = LLMProvider.GEMINI
    settings.gemini_api_key = SecretStr("test_api_key")
    test_model = "gemini-test-model"

    llm = GeminiLLM(model=test_model, temperature=0.5)
    
    messages = [
        LLMMessage(role="system", content="Be helpful."),
        LLMMessage(role="user", content="Previous message"),
        LLMMessage(role="assistant", content="Previous response"),
        LLMMessage(role="user", content="Hello"),
    ]

    # Act
    response = llm.chat(messages)

    # Assert
    mock_gemini_client["configure"].assert_called_once_with(api_key="test_api_key")
    
    mock_gemini_client["model_class"].assert_called_once_with(
        model_name=test_model,
        generation_config={"temperature": 0.5},
        system_instruction="Be helpful.",
    )
    
    expected_history = [
        {"role": "user", "parts": ["Previous message"]},
        {"role": "model", "parts": ["Previous response"]},
    ]
    mock_gemini_client["model_instance"].start_chat.assert_called_once_with(
        history=expected_history
    )

    mock_gemini_client["chat_session"].send_message.assert_called_once_with("Hello")
    
    assert response.content == "This is a Gemini response."
    assert response.model == test_model
    assert response.usage["prompt_tokens"] == 10
    assert response.usage["total_tokens"] == 30


def test_gemini_llm_init_raises_error_if_no_key():
    """Test that GeminiLLM raises a ValueError if the API key is not set."""
    # Arrange
    settings.llm_provider = LLMProvider.GEMINI
    settings.gemini_api_key = None  # Ensure key is not set

    # Act & Assert
    with pytest.raises(ValueError, match="GEMINI_API_KEY is not set."):
        GeminiLLM(model="test-model")


def test_gemini_llm_stream_chat(mock_gemini_client):
    """Test the stream_chat method of the GeminiLLM provider."""
    # Arrange
    settings.llm_provider = LLMProvider.GEMINI
    settings.gemini_api_key = SecretStr("test_api_key")
    test_model = "gemini-test-model"

    llm = GeminiLLM(model=test_model, temperature=0.5)

    messages = [
        LLMMessage(role="system", content="Be concise."),
        LLMMessage(role="user", content="Tell me a story"),
    ]

    # Mock streaming response chunks
    mock_chunk1 = MagicMock()
    mock_chunk1.text = "Once upon "
    mock_chunk2 = MagicMock()
    mock_chunk2.text = "a time..."
    mock_chunk3 = MagicMock()
    mock_chunk3.text = " The end."

    mock_gemini_client["chat_session"].send_message.return_value = iter(
        [mock_chunk1, mock_chunk2, mock_chunk3]
    )

    # Act
    chunks = list(llm.stream_chat(messages))

    # Assert
    mock_gemini_client["configure"].assert_called_with(api_key="test_api_key")

    mock_gemini_client["model_class"].assert_called_with(
        model_name=test_model,
        generation_config={"temperature": 0.5},
        system_instruction="Be concise.",
    )

    mock_gemini_client["model_instance"].start_chat.assert_called_with(history=[])

    mock_gemini_client["chat_session"].send_message.assert_called_once_with(
        "Tell me a story", stream=True
    )

    assert chunks == ["Once upon ", "a time...", " The end."]
