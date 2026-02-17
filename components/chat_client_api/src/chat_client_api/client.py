"""Abstract base class defining the ChatClient contract."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from chat_client_api.models import Channel, Message


class ChatClient(ABC):
    """Abstract contract for a Chat client."""

    @abstractmethod
    def get_channels(self) -> list[Channel]:
        """Retrieve all accessible channels."""

    @abstractmethod
    def get_messages(self, channel_id: str, limit: int = 10) -> list[Message]:
        """Retrieve recent messages from a channel."""

    @abstractmethod
    def send_message(self, channel_id: str, content: str) -> Message:
        """Send a message to a channel."""
        
from collections.abc import Callable

_client_factory: Callable[[], ChatClient] | None = None


def register_client_factory(factory: Callable[[], ChatClient]) -> None:
    global _client_factory
    _client_factory = factory


def get_client() -> ChatClient:
    if _client_factory is None:
        raise RuntimeError("No ChatClient implementation registered.")
    return _client_factory()
