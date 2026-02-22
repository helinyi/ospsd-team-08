"""Concrete Discord implementation of the ChatClient interface (minimal stub)."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from chat_client_api.client import ChatClient
from chat_client_api.models import Channel, Message


class DiscordClient(ChatClient):
    """Discord implementation of the ChatClient abstract interface.

    Note: This is a minimal in-memory implementation for HW1.
    """

    def __init__(self) -> None:
        """Initialize the Discord client (in-memory)."""
        self._channels: list[Channel] = [
            Channel(id="general", name="general", topic="Default channel")
        ]
        self._messages_by_channel: dict[str, list[Message]] = {"general": []}

    def get_channels(self) -> list[Channel]:
        """Retrieve all accessible channels."""
        return list(self._channels)

    def get_messages(self, channel_id: str, limit: int = 10) -> list[Message]:
        """Retrieve recent messages from a channel."""
        messages = self._messages_by_channel.get(channel_id, [])
        return list(messages[-limit:])

    def send_message(self, channel_id: str, content: str) -> Message:
        """Send a message to a channel."""
        msg = Message(
            id=str(uuid4()),
            channel_id=channel_id,
            sender="me",
            content=content,
            timestamp=datetime.now(timezone.utc),
        )
        self._messages_by_channel.setdefault(channel_id, []).append(msg)
        return msg