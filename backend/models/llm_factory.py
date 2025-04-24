"""
Factory for creating LLM instances based on configuration.
"""

from typing import Optional

from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.language_models.chat_models import BaseChatModel

from config import (
    ModelConfig,
    ModelProvider,
    OpenAIConfig,
    AnthropicConfig,
    GoogleConfig,
)


class LLMFactory:
    """Factory for creating LLM instances from configuration."""

    @staticmethod
    def create_llm(config: ModelConfig) -> BaseChatModel:
        """
        Create an LLM instance based on the provided configuration.

        Args:
            config: Model configuration

        Returns:
            A LangChain chat model instance

        Raises:
            ValueError: If the provider is not supported
        """
        if config.provider == ModelProvider.OPENAI:
            if not isinstance(config, OpenAIConfig):
                raise ValueError("Expected OpenAIConfig for OpenAI provider")

            return ChatOpenAI(
                model=config.model_name,
                openai_api_key=config.api_key,
                streaming=True,
                temperature=0.7,
            )

        elif config.provider == ModelProvider.ANTHROPIC:
            if not isinstance(config, AnthropicConfig):
                raise ValueError("Expected AnthropicConfig for Anthropic provider")

            return ChatAnthropic(
                model=config.model_name,
                anthropic_api_key=config.api_key,
                streaming=True,
                temperature=0.7,
            )

        elif config.provider == ModelProvider.GOOGLE:
            if not isinstance(config, GoogleConfig):
                raise ValueError("Expected GoogleConfig for Google provider")

            return ChatGoogleGenerativeAI(
                model=config.model_name,
                google_api_key=config.api_key,
                temperature=0.7,
            )

        else:
            raise ValueError(f"Unsupported provider: {config.provider}")

    @staticmethod
    def create_from_params(
        provider: str, model_name: str, api_key: Optional[str] = None
    ) -> BaseChatModel:
        """
        Create an LLM instance based on provider, model name, and API key.

        Args:
            provider: Model provider name
            model_name: Model name
            api_key: API key for the provider

        Returns:
            A LangChain chat model instance
        """
        provider_enum = ModelProvider(provider)

        if provider_enum == ModelProvider.OPENAI:
            config = OpenAIConfig(model_name=model_name, api_key=api_key)
        elif provider_enum == ModelProvider.ANTHROPIC:
            config = AnthropicConfig(model_name=model_name, api_key=api_key)
        elif provider_enum == ModelProvider.GOOGLE:
            config = GoogleConfig(model_name=model_name, api_key=api_key)
        else:
            raise ValueError(f"Unsupported provider: {provider}")

        return LLMFactory.create_llm(config)
