"""Concrete Discord implementation of the ChatClient interface."""

from __future__ import annotations

from typing import TYPE_CHECKING

from chat_client_api.client import ChatClient

if TYPE_CHECKING:
    from chat_client_api.models import Channel, Message


class DiscordClient(ChatClient):
    """Discord implementation of the ChatClient abstract interface."""
    def __init__(self) -> None:
        """Initialize the Discord client."""
        pass
        
    def get_channels(self) -> list[Channel]:
        """Retrieve all accessible channels."""
        msg = "Not implemented yet"
        raise NotImplementedError(msg)

    def get_messages(self, channel_id: str, limit: int = 10) -> list[Message]:
        """Retrieve recent messages from a channel."""
        msg = "Not implemented yet"
        raise NotImplementedError(msg)

    def send_message(self, channel_id: str, content: str) -> Message:
        """Send a message to a channel."""
        msg = "Not implemented yet"
        raise NotImplementedError(msg)
