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
        general = Channel(id="general", name="general")
        self._channels: list[Channel] = [
            general
        ]
        self._messages_by_channel: dict[Channel, list[Message]] = {general: []}

    def _validate_channel_exists(self, channel: Channel) -> None:
        """Validate that a channel exists.

        Args:
            channel: The channel to validate.

        Raises:
            ValueError: If the channel does not exist.

        """
        if not any(channel.id == c.id for c in self._channels):
            msg = f"Channel with id '{channel.id}' does not exist."
            raise ValueError(msg)

    def get_channels(self) -> list[Channel]:
        """Retrieve all accessible channels."""
        return list(self._channels)

    def get_messages(self, channel: Channel, limit: int = 10) -> list[Message]:
        """Retrieve recent messages from a channel.

        Args:
            channel: The channel object.
            limit: Maximum number of messages to retrieve.

        Returns:
            A list of recent messages from the channel.

        Raises:
            ValueError: If the channel does not exist.

        """
        self._validate_channel_exists(channel)
        messages = self._messages_by_channel.get(channel, [])
        return list(messages[-limit:])

    def send_message(self, channel: Channel, content: str) -> Message:
        """Send a message to a channel.

        Args:
            channel: The channel to send to.
            content: The message content.

        Returns:
            The sent message.

        Raises:
            ValueError: If the channel does not exist.

        """
        self._validate_channel_exists(channel)
        msg = Message(
            id=str(uuid4()),
            channel=channel,
            sender="me",
            content=content,
            timestamp=datetime.now(UTC),
        )
        self._messages_by_channel.setdefault(channel, []).append(msg)
        return msg
