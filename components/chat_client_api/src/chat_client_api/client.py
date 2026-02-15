"""Core chat client definitions."""

from abc import ABC, abstractmethod


class ChatClient(ABC):
    """Abstract base class for chat clients."""

    @abstractmethod
    def send_message(self, channel: str, message: str) -> None:
        """Send a message."""
        pass


# for dependency injection
_client_factory = None


def register_client(factory_func):
    """Register a client factory."""
    global _client_factory
    _client_factory = factory_func


def get_client() -> ChatClient:
    """Return an instance of chat client."""
    if _client_factory is None:
        raise RuntimeError("No client implementation found!")

    return _client_factory()
