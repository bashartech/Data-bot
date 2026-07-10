from agents.models.interface import Model, ModelProvider
from agents.models.openai_provider import OpenAIProvider

from config.settings import settings


class GroqModelProvider(ModelProvider):
    def __init__(self):
        self._provider = OpenAIProvider(
            base_url="https://api.groq.com/openai/v1",
            api_key=settings.groq_api_key,
        )

    def get_model(self, model_name: str | None) -> Model:
        return self._provider.get_model(model_name or settings.groq_model)
