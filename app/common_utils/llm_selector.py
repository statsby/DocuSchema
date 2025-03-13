import os
from typing import Any
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from langchain_huggingface import ChatHuggingFace
from langchain_cohere import ChatCohere
from app.common_utils.loggers import logger
from app.config.config import Config


class ConfigurationError(Exception):
    """Custom exception for configuration errors in LLMSelector."""
    pass


class LLMSelector:
    """
    LLMSelector dynamically selects and initializes a language model based on the configuration.

    Supported formats for `LLM_MODEL_NAME` (case-insensitive):
        - "openai:gpt-4" → Uses OpenAI's GPT-4
        - "ollama:llama3" → Uses Ollama's LLaMA-3
        - "huggingface:mistral-7b" → Uses Hugging Face's Mistral-7B
        - "cohere:command-r" → Uses Cohere's Command-R+
    """

    def __init__(self) -> None:
        self.model_name: str = (Config.LLM_MODEL_NAME or "").strip().lower()
        logger.info(f"LLMSelector initialized with model: '{self.model_name}'")

    def get_llm_model(self) -> Any:
        """
        Selects and initializes an LLM based on the `LLM_MODEL_NAME` format.

        Returns:
            Any: An instance of the selected language model.

        Raises:
            ConfigurationError: If the configuration is missing, incorrectly formatted, or unsupported.
        """
        if not self.model_name:
            logger.error("LLM model name is missing. Please update your .env file.")
            raise ConfigurationError("LLM model name is missing. Please update your .env file.")

        try:

            provider, model_id = map(str.strip, self.model_name.split(":", 1))
        except ValueError:
            logger.error("LLM model name must be in the format 'provider:model'.")
            raise ConfigurationError("LLM model name must be in the format 'provider:model'.")

        if not model_id:
            logger.error(f"Model name is missing after provider '{provider}'.")
            raise ConfigurationError(f"Model name is missing after provider '{provider}'.")

        logger.info(f"Selecting LLM model: provider '{provider}', model '{model_id}'")

        model_initializers = {
            "openai": self._initialize_openai,
            "ollama": self._initialize_ollama,
            "huggingface": self._initialize_huggingface,
            "cohere": self._initialize_cohere,
        }

        if provider in model_initializers:
            return model_initializers[provider](model_id)

        logger.error(f"Unsupported LLM model: '{self.model_name}'. Supported models: OpenAI, Ollama, Hugging Face, Cohere.")
        raise ConfigurationError(
            f"Unsupported LLM model: '{self.model_name}'. Supported models: OpenAI, Ollama, Hugging Face, Cohere. "
            "Update .env with correct syntax (e.g., 'openai:gpt-4')."
        )

    def _initialize_openai(self, model_id: str) -> ChatOpenAI:
        """Initializes an OpenAI model."""
        self._validate_api_key()
        logger.info(f"Initializing OpenAI model: '{model_id}'")
        return ChatOpenAI(model=model_id, api_key=Config.API_KEY, temperature=0.0)

    def _initialize_ollama(self, model_id: str) -> ChatOllama:
        """Initializes an Ollama model."""
        logger.info(f"Initializing Ollama model: '{model_id}'")
        return ChatOllama(model=model_id)

    def _initialize_huggingface(self, model_id: str) -> ChatHuggingFace:
        """Initializes a Hugging Face model."""
        self._validate_api_key()
        logger.info(f"Initializing Hugging Face model: '{model_id}'")
        return ChatHuggingFace(repo_id=model_id, api_key=Config.API_KEY, temperature=0.0)

    def _initialize_cohere(self, model_id: str) -> ChatCohere:
        """Initializes a Cohere model."""
        self._validate_api_key()
        logger.info(f"Initializing Cohere model: '{model_id}'")
        return ChatCohere(model=model_id, api_key=Config.API_KEY, temperature=0.0)

    @staticmethod
    def _validate_api_key() -> None:
        """Validates the presence of an API key in the configuration."""
        if not Config.API_KEY:
            logger.error("API key is missing. Update your .env file.")
            raise ConfigurationError("API key is missing.")
