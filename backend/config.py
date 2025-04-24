"""
Configuration settings for the conversational AI application.
"""

from enum import Enum
from typing import Dict, Optional


class ModelProvider(str, Enum):
    """Available model providers."""

    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"


class ModelConfig:
    """Base model configuration class."""

    def __init__(self, provider: ModelProvider, api_key: Optional[str] = None):
        self.provider = provider
        self.api_key = api_key


class OpenAIConfig(ModelConfig):
    """Configuration for OpenAI models."""

    def __init__(
        self, model_name: str = "gpt-3.5-turbo", api_key: Optional[str] = None
    ):
        super().__init__(provider=ModelProvider.OPENAI, api_key=api_key)
        self.model_name = model_name


class AnthropicConfig(ModelConfig):
    """Configuration for Anthropic models."""

    def __init__(
        self, model_name: str = "claude-3-opus-20240229", api_key: Optional[str] = None
    ):
        super().__init__(provider=ModelProvider.ANTHROPIC, api_key=api_key)
        self.model_name = model_name


class GoogleConfig(ModelConfig):
    """Configuration for Google models."""

    def __init__(self, model_name: str = "gemini-pro", api_key: Optional[str] = None):
        super().__init__(provider=ModelProvider.GOOGLE, api_key=api_key)
        self.model_name = model_name


# Available models by provider
AVAILABLE_MODELS = {
    ModelProvider.OPENAI: [
        "gpt-4.1-2025-04-14",
        "gpt-4-0613",
        "gpt-4.5-preview-2025-02-27",
        "gpt-4-turbo-2024-04-09",
    ],
    ModelProvider.ANTHROPIC: [
        "claude-3-7-sonnet-20250219",
        "claude-3-5-sonnet-20240620",
        "claude-3-5-haiku-20241022",
    ],
    ModelProvider.GOOGLE: [
        "gemini-2.0-flash-lite",
        "gemini-2.0-flash",
        "gemini-2.5-pro-preview-03-25",
    ],
}

# Default system prompt for the conversational AI
DEFAULT_SYSTEM_PROMPT = """You are a helpful, friendly AI assistant. Answer the user's questions to the best of your ability."""
