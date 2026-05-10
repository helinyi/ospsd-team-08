"""Adapter implementation for the chat client service."""

from __future__ import annotations

from typing import TYPE_CHECKING

from chat_client_api import Channel as ApiChannel
from chat_client_api import ChatClient
from chat_client_api import Message as ApiMessage
from fast_api_client.api.default.get_channel_messages_channels_channel_id_messages_get import (
    sync as get_messages_sync,
)
from fast_api_client.api.default.get_channels_channels_get import (
    sync as get_channels_sync,
)
from fast_api_client.api.default.send_channel_message_channels_channel_id_messages_post import (
    sync as send_message_sync,
)
from fast_api_client.client import Client
from fast_api_client.models.body_send_channel_message_channels_channel_id_messages_post import (
    BodySendChannelMessageChannelsChannelIdMessagesPost,
)
from fast_api_client.models.http_validation_error import HTTPValidationError
from fast_api_client.types import Unset

if TYPE_CHECKING:
    from fast_api_client.models.channel import Channel as GeneratedChannel
    from fast_api_client.models.message import Message as GeneratedMessage


class ChatClientAdapter(ChatClient):
    """Adapter that exposes the remote Discord service via the ChatClient API."""

    def __init__(self, base_url: str) -> None:
        """Initialize the adapter with the base URL of the remote service."""
        self._client = Client(base_url=base_url)

    def get_channels(self) -> list[ApiChannel]:
        """Retrieve all accessible channels."""
        response = get_channels_sync(client=self._client)
        if response is None:
            msg = "Failed to fetch channels from the service."
            raise RuntimeError(msg)
        return [self._to_api_channel(channel) for channel in response]

    def get_channel(self, channel_id: str) -> ApiChannel:
        """Get a single channel by ID.

        Args:
            channel_id: The channel ID to retrieve.

        Returns:
            Channel object.

        Raises:
            RuntimeError: If the service call fails.

        """
        channels = self.get_channels()
        target = next((c for c in channels if c.channel_id == channel_id), None)
        if target is None:
            msg = f"Channel with id '{channel_id}' not found."
            raise ValueError(msg)
        return target

    def get_messages(
        self,
        channel_id: str,
        limit: int = 10,
        cursor: str | None = None,   # noqa: ARG002 - cursor pagination not supported by Discord API
    ) -> list[ApiMessage]:
        """Retrieve recent messages from a channel.

        Args:
            channel_id: The channel ID to fetch messages from.
            limit: Maximum number of messages to return.
            cursor: Optional pagination cursor (ignored).

        """
        response = get_messages_sync(
            channel_id=channel_id,
            client=self._client,
            limit=limit,
        )
        if response is None:
            msg = "Failed to fetch messages from the service."
            raise RuntimeError(msg)
        if isinstance(response, HTTPValidationError):
            msg = "Service rejected get_messages request."
            raise TypeError(msg)
        return [self._to_api_message(message) for message in response]

    def get_message(self, message_id: str) -> ApiMessage:
        """Get a single message by its opaque ID.

        Args:
            message_id: Opaque message ID in format 'channel_id:message_id'.

        Returns:
            Message object.

        Raises:
            ValueError: If the message is not found.

        """
        try:
            channel_id, _ = message_id.split(":", 1)
        except ValueError as exc:
            msg = f"Invalid message_id format: '{message_id}'. Expected 'channel_id:message_id'."
            raise ValueError(msg) from exc
        messages = self.get_messages(channel_id)
        target = next((m for m in messages if m.message_id == message_id), None)
        if target is None:
            msg = f"Message with id '{message_id}' not found."
            raise ValueError(msg)
        return target

    def send_message(self, channel_id: str, text: str) -> ApiMessage:
        """Send a message to a channel.

        Args:
            channel_id: The channel ID to send to.
            text: The message content.

        """
        body = BodySendChannelMessageChannelsChannelIdMessagesPost(content=text)
        response = send_message_sync(
            channel_id=channel_id,
            client=self._client,
            body=body,
        )
        if response is None:
            msg = "Failed to send message through the service."
            raise RuntimeError(msg)
        if isinstance(response, HTTPValidationError):
            msg = "Service rejected send_message request."
            raise TypeError(msg)
        return self._to_api_message(response)

    def delete_message(self, message_id: str) -> None:
        """Delete a message by its opaque ID.

        Args:
            message_id: Opaque message ID. Not supported by this adapter.

        Raises:
            NotImplementedError: delete_message is not supported via the service adapter.

        """
        msg = "delete_message is not supported via the service adapter."
        raise NotImplementedError(msg)

    @staticmethod
    def _to_api_channel(channel: GeneratedChannel) -> ApiChannel:
        """Convert a generated service Channel into an API Channel."""
        topic = None if channel.topic is None or isinstance(channel.topic, Unset) else channel.topic  # noqa: F841
        return ApiChannel(
            channel_id=str(channel.id),
            name=str(channel.name),
        )

    @staticmethod
    def _to_api_message(message: GeneratedMessage) -> ApiMessage:
        """Convert a generated service Message into an API Message."""
        return ApiMessage(
            message_id=str(message.id),
            channel=str(message.channel.id) if hasattr(message.channel, "id") else str(message.channel),
            sender=str(message.sender),
            text=str(message.content),
            timestamp=message.timestamp,
        )
