"""Mock LLM provider for testing without Ollama."""
import logging
from typing import List, Iterator, Any
from .base import BaseLLMProvider, LLMMessage, LLMResponse

logger = logging.getLogger(__name__)


class MockProvider(BaseLLMProvider):
    """Mock LLM provider for testing."""

    def __init__(
        self,
        model: str = "mock-model",
        temperature: float = 0.3,
        **kwargs: Any
    ):
        super().__init__(model, temperature, **kwargs)
        logger.info(f"Initialized Mock provider with model: {model}")

    def chat(
        self,
        messages: List[LLMMessage],
        **kwargs: Any
    ) -> LLMResponse:
        """Return mock tailored response.

        Args:
            messages: Conversation messages
            **kwargs: Additional options

        Returns:
            LLMResponse with mock tailored content
        """
        # Extract the user prompt to understand context
        user_message = next((m.content for m in messages if m.role == "user"), "")

        # Check if this is a keyword extraction request
        if "Extract" in user_message and "keywords" in user_message:
            content = """keywords:
  - Python
  - Go
  - Kubernetes
  - Docker
  - Microservices
  - AWS
  - PostgreSQL
  - Redis
  - Distributed Systems
  - CI/CD
  - Terraform
  - Infrastructure as Code"""
        else:
            # This is a tailoring request
            content = """experience:
  - company: Tech Corp
    position: Senior Software Engineer
    location: San Francisco, CA
    start_date: "2020-01"
    end_date: "2024-12"
    highlights:
      - "Led team of **5 engineers** building **microservices platform** serving **10M+ users** with focus on **cloud infrastructure**"
      - "**Improved** API response time by **40%** through **Redis caching** and **PostgreSQL** query optimization"
      - "Designed and implemented **CI/CD pipeline** using **GitHub Actions** and **Terraform**, **reducing** deployment time from hours to minutes"
      - "Architected **Kubernetes**-based container orchestration system supporting **distributed systems** at scale"
      - "**Mentored** 3 junior engineers on **distributed systems** best practices and **microservices architecture**"

  - company: Startup Inc
    position: Software Engineer
    location: Remote
    start_date: "2019-06"
    end_date: "2020-01"
    highlights:
      - "Built real-time analytics dashboard using **React** and **WebSockets** for **cloud infrastructure** monitoring"
      - "Implemented OAuth2 authentication system handling **100K+ users** with **PostgreSQL** backend"
      - "**Reduced** database query time by **60%** through indexing and denormalization using **PostgreSQL** and **Redis**"
      - "Developed **Docker**-based deployment system improving development workflow efficiency"

skills:
  - label: Languages & Core
    details: "**Python**, **Go**, JavaScript, TypeScript, SQL"
  - label: Cloud & Infrastructure
    details: "**Kubernetes**, **Docker**, **AWS**, **Terraform**, GitHub Actions, **CI/CD**"
  - label: Databases & Caching
    details: "**PostgreSQL**, **Redis**, MongoDB, Elasticsearch"
  - label: Architecture
    details: "**Microservices**, **Distributed Systems**, RESTful APIs, Message Queues"

bold_keywords:
  - Python
  - Go
  - Kubernetes
  - Docker
  - Microservices
  - AWS
  - PostgreSQL
  - Redis
  - Distributed Systems
  - CI/CD
  - Terraform
  - Infrastructure as Code
  - Cloud Infrastructure"""

        return LLMResponse(
            content=content,
            model=self.model,
            usage={
                "prompt_tokens": 500,
                "completion_tokens": 800,
            },
            metadata={
                "mock": True,
                "note": "This is a mock response for testing"
            }
        )

    def stream_chat(
        self,
        messages: List[LLMMessage],
        **kwargs: Any
    ) -> Iterator[str]:
        """Stream mock response.

        Yields:
            Chunks of response text
        """
        response = self.chat(messages, **kwargs)
        # Yield the full content at once for simplicity
        yield response.content
