import os
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from langchain_huggingface import ChatHuggingFace
from langchain_cohere import ChatCohere
from common_utils.loggers import logger
from config.config import LLM_MODEL_NAME, API_KEY

class LLMSelector:
    """
    LLMSelector dynamically selects and initializes a language model based on the configuration.

    This class reads the `LLM_MODEL_NAME` from the environment variables and initializes the 
    corresponding model from OpenAI, Ollama, Hugging Face, or Cohere.

    Supported formats for `LLM_MODEL_NAME`:
        - "openai:gpt-4" → Uses OpenAI's GPT-4
        - "ollama:llama3" → Uses Ollama's LLaMA-3
        - "huggingface:mistral-7b" → Uses Hugging Face's Mistral-7B
        - "cohere:command-r" → Uses Cohere's Command-R+

    Note:
        - If an API key is required (e.g., OpenAI, Hugging Face, Cohere), it must be set in `.env`.
        - If the model name is missing or incorrectly formatted, an error is raised.
        - We can easily extend this class to support additional language models in the future based on the LLM of your choice as langchain supports variety of LLM Models.
    """

    def __init__(self):
        self.model_name = (LLM_MODEL_NAME or "").strip().lower()
        logger.info(f"LLMSelector initialized with model: '{self.model_name}'")

    def get_llm_model(self):
        """
        Selects and initializes an LLM based on the `LLM_MODEL_NAME` prefix.

        Returns:
            An instance of the selected language model class.

        Raises:
            ValueError: If the model name is missing, incorrectly formatted, or unsupported.
        """
        try:
            if not self.model_name:
                logger.error("LLM model name is missing. Please update your .env file.")
                raise ValueError("LLM model name is missing. Update your .env file.")

            logger.info(f"Selecting LLM model: '{self.model_name}'")

            if "openai" in self.model_name:
                if not API_KEY:
                    logger.error("OpenAI API key is missing. Update your .env file.")
                    raise ValueError("OpenAI API key is missing.")

                model_id = self.model_name.replace("openai:", "").strip()
                if not model_id:
                    logger.error("OpenAI model name is missing after 'openai:'. Specify a valid model (e.g., 'openai:gpt-4').")
                    raise ValueError("OpenAI model name is missing. Specify a valid model (e.g., 'openai:gpt-4').")

                logger.info(f"Initializing OpenAI model: '{model_id}'")
                return ChatOpenAI(model=model_id, api_key=API_KEY, temperature=0.0)

            elif "ollama" in self.model_name:
                model_id = self.model_name.replace("ollama:", "").strip()
                if not model_id:
                    logger.error("Ollama model name is missing after 'ollama:'.")
                    raise ValueError("Ollama model name is missing.")

                logger.info(f"Initializing Ollama model: '{model_id}'")
                return ChatOllama(model=model_id)

            elif "huggingface" in self.model_name:
                if not API_KEY:
                    logger.error("Hugging Face API key is missing. Update your .env file.")
                    raise ValueError("Hugging Face API key is missing.")

                model_id = self.model_name.replace("huggingface:", "").strip()
                if not model_id:
                    logger.error("Hugging Face model name is missing after 'huggingface:'.")
                    raise ValueError("Hugging Face model name is missing.")

                logger.info(f"Initializing Hugging Face model: '{model_id}'")
                return ChatHuggingFace(repo_id=model_id, api_key=API_KEY, temperature=0.0)

            elif "cohere" in self.model_name:
                if not API_KEY:
                    logger.error("Cohere API key is missing. Update your .env file.")
                    raise ValueError("Cohere API key is missing.")

                model_id = self.model_name.replace("cohere:", "").strip()
                if not model_id:
                    logger.error("Cohere model name is missing after 'cohere:'.")
                    raise ValueError("Cohere model name is missing.")

                logger.info(f"Initializing Cohere model: {model_id}")
                return ChatCohere(model=model_id, api_key=API_KEY, temperature=0.0)

            else:
                logger.error(f"Unsupported LLM model. Supported models: OpenAI, Ollama, Hugging Face, Cohere. Update .env with correct syntax (e.g., openai:gpt-4o).")
                raise ValueError(f"Unsupported LLM model. Supported models: OpenAI, Ollama, Hugging Face, Cohere. Update .env with correct syntax (e.g., openai:gpt-4o).")

        except ValueError as e:
            logger.error(f"Configuration Error: {e}")
            raise

        except Exception as e:
            logger.error("Critical Error: Unexpected failure while initializing LLM.")
            logger.exception(e)
            raise ValueError("A critical error occurred while initializing LLM. Check logs for details.")
