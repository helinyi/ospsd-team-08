from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import patch

import pytest

from chat_client_api.models import Channel as ApiChannel
from chat_client_api.models import Message as ApiMessage
from chat_client_adapter.adapter import ChatClientAdapter
from discord_service_api_client.fast_api_client.models.body_send_channel_message_channels_channel_id_messages_post import (
    BodySendChannelMessageChannelsChannelIdMessagesPost,
)
from discord_service_api_client.fast_api_client.models.channel import (
    Channel as GeneratedChannel,
)
from discord_service_api_client.fast_api_client.models.http_validation_error import (
    HTTPValidationError,
)
from discord_service_api_client.fast_api_client.models.message import (
    Message as GeneratedMessage,
)


def make_generated_channel(
    channel_id: str = "123",
    name: str = "general",
    topic: str | None = None,
) -> GeneratedChannel:
    return GeneratedChannel(
        id=channel_id,
        name=name,
        topic=topic,
    )


def make_generated_message(
    message_id: str = "m1",
    channel: GeneratedChannel | None = None,
    sender: str = "me",
    content: str = "hello",
    timestamp: datetime | None = None,
) -> GeneratedMessage:
    return GeneratedMessage(
        id=message_id,
        channel=channel if channel is not None else make_generated_channel(),
        sender=sender,
        content=content,
        timestamp=timestamp if timestamp is not None else datetime.now(UTC),
    )


def test_get_channels_returns_api_channels() -> None:
    adapter = ChatClientAdapter(base_url="http://example.com")
    generated_channels = [
        make_generated_channel(channel_id="1", name="general", topic="welcome"),
        make_generated_channel(channel_id="2", name="random", topic=None),
    ]

    with patch(
        "chat_client_adapter.adapter.get_channels_sync",
        return_value=generated_channels,
    ) as mock_get_channels:
        result = adapter.get_channels()

    mock_get_channels.assert_called_once_with(client=adapter._client)
    assert result == [
        ApiChannel(id="1", name="general", topic="welcome"),
        ApiChannel(id="2", name="random", topic=None),
    ]


def test_get_channels_raises_when_response_is_none() -> None:
    adapter = ChatClientAdapter(base_url="http://example.com")

    with patch(
        "chat_client_adapter.adapter.get_channels_sync",
        return_value=None,
    ):
        with pytest.raises(RuntimeError, match="Failed to fetch channels"):
            adapter.get_channels()


def test_get_messages_returns_api_messages() -> None:
    adapter = ChatClientAdapter(base_url="http://example.com")
    api_channel = ApiChannel(id="123", name="general")
    timestamp = datetime(2026, 3, 31, 12, 0, tzinfo=UTC)

    generated_messages = [
        make_generated_message(
            message_id="m1",
            channel=make_generated_channel(channel_id="123", name="general"),
            sender="alice",
            content="hello",
            timestamp=timestamp,
        ),
        make_generated_message(
            message_id="m2",
            channel=make_generated_channel(channel_id="123", name="general"),
            sender="bob",
            content="hi",
            timestamp=timestamp,
        ),
    ]

    with patch(
        "chat_client_adapter.adapter.get_messages_sync",
        return_value=generated_messages,
    ) as mock_get_messages:
        result = adapter.get_messages(api_channel, limit=25)

    mock_get_messages.assert_called_once_with(
        channel_id="123",
        client=adapter._client,
        limit=25,
    )

    assert result == [
        ApiMessage(
            id="m1",
            channel=ApiChannel(id="123", name="general", topic=None),
            sender="alice",
            content="hello",
            timestamp=timestamp,
        ),
        ApiMessage(
            id="m2",
            channel=ApiChannel(id="123", name="general", topic=None),
            sender="bob",
            content="hi",
            timestamp=timestamp,
        ),
    ]


def test_get_messages_raises_when_response_is_none() -> None:
    adapter = ChatClientAdapter(base_url="http://example.com")
    api_channel = ApiChannel(id="123", name="general")

    with patch(
        "chat_client_adapter.adapter.get_messages_sync",
        return_value=None,
    ):
        with pytest.raises(RuntimeError, match="Failed to fetch messages"):
            adapter.get_messages(api_channel)


def test_get_messages_raises_on_validation_error() -> None:
    adapter = ChatClientAdapter(base_url="http://example.com")
    api_channel = ApiChannel(id="123", name="general")
    validation_error = HTTPValidationError(detail=[])

    with patch(
        "chat_client_adapter.adapter.get_messages_sync",
        return_value=validation_error,
    ):
        with pytest.raises(RuntimeError, match="Service rejected get_messages request"):
            adapter.get_messages(api_channel)


def test_send_message_returns_api_message() -> None:
    adapter = ChatClientAdapter(base_url="http://example.com")
    api_channel = ApiChannel(id="123", name="general")
    timestamp = datetime(2026, 3, 31, 12, 0, tzinfo=UTC)

    generated_message = make_generated_message(
        message_id="m99",
        channel=make_generated_channel(channel_id="123", name="general"),
        sender="me",
        content="test message",
        timestamp=timestamp,
    )

    with patch(
        "chat_client_adapter.adapter.send_message_sync",
        return_value=generated_message,
    ) as mock_send_message:
        result = adapter.send_message(api_channel, "test message")

    mock_send_message.assert_called_once()
    _, kwargs = mock_send_message.call_args

    assert kwargs["channel_id"] == "123"
    assert kwargs["client"] == adapter._client
    assert isinstance(
        kwargs["body"],
        BodySendChannelMessageChannelsChannelIdMessagesPost,
    )
    assert kwargs["body"].content == "test message"

    assert result == ApiMessage(
        id="m99",
        channel=ApiChannel(id="123", name="general", topic=None),
        sender="me",
        content="test message",
        timestamp=timestamp,
    )


def test_send_message_raises_when_response_is_none() -> None:
    adapter = ChatClientAdapter(base_url="http://example.com")
    api_channel = ApiChannel(id="123", name="general")

    with patch(
        "chat_client_adapter.adapter.send_message_sync",
        return_value=None,
    ):
        with pytest.raises(RuntimeError, match="Failed to send message"):
            adapter.send_message(api_channel, "hello")


def test_send_message_raises_on_validation_error() -> None:
    adapter = ChatClientAdapter(base_url="http://example.com")
    api_channel = ApiChannel(id="123", name="general")
    validation_error = HTTPValidationError(detail=[])

    with patch(
        "chat_client_adapter.adapter.send_message_sync",
        return_value=validation_error,
    ):
        with pytest.raises(RuntimeError, match="Service rejected send_message request"):
            adapter.send_message(api_channel, "hello")
