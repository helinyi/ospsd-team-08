"""Adapter implementation for the chat client service."""

from __future__ import annotations

from typing import TYPE_CHECKING

from chat_client_api.client import ChatClient
from chat_client_api.models import Channel as ApiChannel
from chat_client_api.models import Message as ApiMessage
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
from fast_api_client.models.http_validation_error import (
    HTTPValidationError,
)
from fast_api_client.types import Unset

if TYPE_CHECKING:
    from fast_api_client.models.channel import (
        Channel as GeneratedChannel,
    )
    from fast_api_client.models.message import (
        Message as GeneratedMessage,
    )


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

    def get_messages(self, channel: ApiChannel, limit: int = 10) -> list[ApiMessage]:
        """Retrieve recent messages from a channel."""
        response = get_messages_sync(
            channel_id=channel.id,
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

    def send_message(self, channel: ApiChannel, content: str) -> ApiMessage:
        """Send a message to a channel."""
        body = BodySendChannelMessageChannelsChannelIdMessagesPost(content=content)

        response = send_message_sync(
            channel_id=channel.id,
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

    @staticmethod
    def _to_api_channel(channel: GeneratedChannel) -> ApiChannel:
        """Convert a generated service Channel into an API Channel."""
        topic: str | None
        if channel.topic is None or isinstance(channel.topic, Unset):
            topic = None
        else:
            topic = channel.topic
            
        return ApiChannel(
            id=channel.id,
            name=channel.name,
            topic=topic,
        )

    @staticmethod
    def _to_api_message(message: GeneratedMessage) -> ApiMessage:
        """Convert a generated service Message into an API Message."""
        return ApiMessage(
            id=message.id,
            channel=ChatClientAdapter._to_api_channel(message.channel),
            sender=message.sender,
            content=message.content,
            timestamp=message.timestamp,
        )
