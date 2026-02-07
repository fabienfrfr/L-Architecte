from langchain_ollama import ChatOllama
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.ollama import OllamaProvider
from apps.architect.domain.config import config

# new
def get_llm_model() -> OpenAIChatModel:
    """
    Factory creating the correct OpenAIChatModel with OllamaProvider.
    """
    return OpenAIChatModel(
        model_name=config.MODEL_NAME,
        provider=OllamaProvider(base_url=f"{config.OLLAMA_URL}/v1"),
    )

# old : to change
def get_llm(json_mode: bool = True):
    """Factory to get the LLM based on environment."""
    return ChatOllama(
        model=config.MODEL_NAME,
        base_url=config.OLLAMA_URL,
        temperature=0,
        format="json" if json_mode else "",
    )