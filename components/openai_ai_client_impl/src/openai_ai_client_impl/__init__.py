"""OpenAI AI client implementation — registers via dependency injection."""
from ai_client_api import register_client

from openai_ai_client_impl.client import OpenAIAIClient


def _create_openai_client() -> OpenAIAIClient:  # pragma: no cover
    """Create an OpenAIAIClient instance."""
    return OpenAIAIClient()


register_client(_create_openai_client)
