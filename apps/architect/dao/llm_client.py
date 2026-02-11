from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.ollama import OllamaProvider
from apps.architect.domain.config import config

def get_llm_model() -> OpenAIChatModel:
    """
    Factory creating the correct OpenAIChatModel with OllamaProvider.
    """
    return OpenAIChatModel(
        model_name=config.MODEL_NAME,
        provider=OllamaProvider(base_url=f"{config.OLLAMA_URL}/v1"),
    )
