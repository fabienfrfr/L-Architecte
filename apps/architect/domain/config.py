from pydantic_settings import BaseSettings
from pydantic import ConfigDict, Field


class Settings(BaseSettings):
    # Modern Pydantic V2 Configuration
    model_config = ConfigDict(env_file=".env", extra="ignore")

    ENV: str = Field(default="local")
    OLLAMA_URL: str = Field(default="http://localhost:11434")

    @property
    def MODEL_NAME(self) -> str:
        if self.ENV.lower() == "test":
            return "qwen3:0.6b"
        return "nemotron-3-nano:30b"


config = Settings()
