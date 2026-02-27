"""Concrete Discord implementation of the ChatClient interface (minimal stub)."""

from __future__ import annotations

from datetime import UTC, datetime
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
            Channel(id="general", name="general")
        ]
        self._messages_by_channel: dict[str, list[Message]] = {"general": []}

    def _validate_channel_exists(self, channel_id: str) -> None:
        """Validate that a channel exists.

        Args:
            channel_id: The channel ID to validate.

        Raises:
            ValueError: If the channel does not exist.

        """
        if not any(channel.id == channel_id for channel in self._channels):
            msg = f"Channel with id '{channel_id}' does not exist."
            raise ValueError(msg)

    def get_channels(self) -> list[Channel]:
        """Retrieve all accessible channels."""
        return list(self._channels)

    def get_messages(self, channel_id: str, limit: int = 10) -> list[Message]:
        """Retrieve recent messages from a channel.

        Args:
            channel_id: The ID of the channel.
            limit: Maximum number of messages to retrieve.

        Returns:
            A list of recent messages from the channel.

        Raises:
            ValueError: If the channel does not exist.

        """
        self._validate_channel_exists(channel_id)
        messages = self._messages_by_channel.get(channel_id, [])
        return list(messages[-limit:])

    def send_message(self, channel_id: str, content: str) -> Message:
        """Send a message to a channel.

        Args:
            channel_id: The ID of the channel to send to.
            content: The message content.

        Returns:
            The sent message.

        Raises:
            ValueError: If the channel does not exist.

        """
        self._validate_channel_exists(channel_id)
        msg = Message(
            id=str(uuid4()),
            channel_id=channel_id,
            sender="me",
            content=content,
            timestamp=datetime.now(UTC),
        )
        self._messages_by_channel.setdefault(channel_id, []).append(msg)
        return msg
