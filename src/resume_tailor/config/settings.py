"""Application settings using pydantic-settings."""
from enum import Enum
from pathlib import Path
from typing import Optional

from pydantic import SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class LLMProvider(str, Enum):
    """Enum for LLM providers."""

    OLLAMA = "ollama"
    GEMINI = "gemini"


class Settings(BaseSettings):
    """Application configuration from environment variables."""

    # LLM Configuration
    llm_provider: LLMProvider = LLMProvider.OLLAMA
    llm_model: str = "llama3.1:8b"
    llm_base_url: Optional[str] = None
    llm_temperature: float = 0.3
    llm_max_tokens: int = 4000
    gemini_api_key: Optional[SecretStr] = None

    # Paths
    base_resume_path: Path = Path("source/base_resume.yaml")
    static_sections_path: Path = Path("source/static_sections.yaml")
    output_dir: Path = Path("./output")

    # RenderCV
    rendercv_theme: str = "engineeringresumes"

    # Logging
    log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env", env_prefix="RESUME_TAILOR_", case_sensitive=False
    )

    @model_validator(mode="after")
    def validate_llm_config(self) -> "Settings":
        """Validate the LLM configuration based on the selected provider."""
        if self.llm_provider == LLMProvider.GEMINI and not self.gemini_api_key:
            raise ValueError("GEMINI_API_KEY must be set when using the Gemini LLM provider.")
        if self.llm_provider == LLMProvider.OLLAMA and not self.llm_base_url:
            raise ValueError("RESUME_TAILOR_LLM_BASE_URL must be set when using the Ollama LLM provider.")
        return self


# Global settings instance
settings = Settings()
