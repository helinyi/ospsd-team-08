"""Tests for ChatClientAdapter."""
from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import patch

import pytest

from chat_client_api import Channel as ApiChannel
from chat_client_api import Message as ApiMessage
from chat_client_adapter.adapter import ChatClientAdapter
from fast_api_client.models.body_send_channel_message_channels_channel_id_messages_post import (
    BodySendChannelMessageChannelsChannelIdMessagesPost,
)
from fast_api_client.models.channel import Channel as GeneratedChannel
from fast_api_client.models.http_validation_error import HTTPValidationError
from fast_api_client.models.message import Message as GeneratedMessage


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
        ApiChannel(channel_id="1", name="general"),
        ApiChannel(channel_id="2", name="random"),
    ]


def test_get_channels_raises_when_response_is_none() -> None:
    adapter = ChatClientAdapter(base_url="http://example.com")

    with (
        patch(
            "chat_client_adapter.adapter.get_channels_sync",
            return_value=None,
        ),
        pytest.raises(RuntimeError, match="Failed to fetch channels"),
    ):
        adapter.get_channels()


def test_get_channel_returns_channel() -> None:
    adapter = ChatClientAdapter(base_url="http://example.com")
    generated_channels = [
        make_generated_channel(channel_id="123", name="general"),
    ]

    with patch(
        "chat_client_adapter.adapter.get_channels_sync",
        return_value=generated_channels,
    ):
        result = adapter.get_channel("123")

    assert isinstance(result, ApiChannel)
    assert result.channel_id == "123"
    assert result.name == "general"


def test_get_channel_raises_when_not_found() -> None:
    adapter = ChatClientAdapter(base_url="http://example.com")

    with (
        patch(
            "chat_client_adapter.adapter.get_channels_sync",
            return_value=[],
        ),
        pytest.raises(ValueError, match="not found"),
    ):
        adapter.get_channel("nope")


def test_get_messages_returns_api_messages() -> None:
    adapter = ChatClientAdapter(base_url="http://example.com")
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
        result = adapter.get_messages("123", limit=25)

    mock_get_messages.assert_called_once_with(
        channel_id="123",
        client=adapter._client,
        limit=25,
    )

    assert len(result) == 2
    assert result[0].message_id == "m1"
    assert result[0].sender == "alice"
    assert result[0].text == "hello"
    assert result[0].channel == "123"
    assert result[1].message_id == "m2"
    assert result[1].sender == "bob"


def test_get_messages_raises_when_response_is_none() -> None:
    adapter = ChatClientAdapter(base_url="http://example.com")

    with (
        patch(
            "chat_client_adapter.adapter.get_messages_sync",
            return_value=None,
        ),
        pytest.raises(RuntimeError, match="Failed to fetch messages"),
    ):
        adapter.get_messages("123")


def test_get_messages_raises_on_validation_error() -> None:
    adapter = ChatClientAdapter(base_url="http://example.com")
    validation_error = HTTPValidationError(detail=[])

    with (
        patch(
            "chat_client_adapter.adapter.get_messages_sync",
            return_value=validation_error,
        ),
        pytest.raises(TypeError, match="Service rejected get_messages request"),
    ):
        adapter.get_messages("123")


def test_send_message_returns_api_message() -> None:
    adapter = ChatClientAdapter(base_url="http://example.com")
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
        result = adapter.send_message("123", "test message")

    mock_send_message.assert_called_once()
    _, kwargs = mock_send_message.call_args
    assert kwargs["channel_id"] == "123"
    assert kwargs["client"] == adapter._client
    assert isinstance(kwargs["body"], BodySendChannelMessageChannelsChannelIdMessagesPost)
    assert kwargs["body"].content == "test message"

    assert isinstance(result, ApiMessage)
    assert result.message_id == "m99"
    assert result.text == "test message"
    assert result.sender == "me"
    assert result.channel == "123"


def test_send_message_raises_when_response_is_none() -> None:
    adapter = ChatClientAdapter(base_url="http://example.com")

    with (
        patch(
            "chat_client_adapter.adapter.send_message_sync",
            return_value=None,
        ),
        pytest.raises(RuntimeError, match="Failed to send message"),
    ):
        adapter.send_message("123", "hello")


def test_send_message_raises_on_validation_error() -> None:
    adapter = ChatClientAdapter(base_url="http://example.com")
    validation_error = HTTPValidationError(detail=[])

    with (
        patch(
            "chat_client_adapter.adapter.send_message_sync",
            return_value=validation_error,
        ),
        pytest.raises(TypeError, match="Service rejected send_message request"),
    ):
        adapter.send_message("123", "hello")


def test_delete_message_raises_not_implemented() -> None:
    adapter = ChatClientAdapter(base_url="http://example.com")
    with pytest.raises(NotImplementedError, match="delete_message is not supported"):
        adapter.delete_message("123:m1")

def test_get_message_returns_message() -> None:
    adapter = ChatClientAdapter(base_url="http://example.com")
    timestamp = datetime(2026, 3, 31, 12, 0, tzinfo=UTC)
    generated_messages = [
        make_generated_message(
            message_id="123:m1",
            channel=make_generated_channel(channel_id="123", name="general"),
            sender="alice",
            content="hello",
            timestamp=timestamp,
        ),
    ]

    with patch(
        "chat_client_adapter.adapter.get_messages_sync",
        return_value=generated_messages,
    ):
        result = adapter.get_message("123:m1")

    assert isinstance(result, ApiMessage)
    assert result.message_id == "123:m1"


def test_get_message_raises_on_invalid_format() -> None:
    adapter = ChatClientAdapter(base_url="http://example.com")
    with pytest.raises(ValueError, match="Invalid message_id format"):
        adapter.get_message("invalid-no-colon")


def test_to_api_message_with_channel_object() -> None:
    """Test _to_api_message when channel is a GeneratedChannel object."""
    timestamp = datetime(2026, 3, 31, 12, 0, tzinfo=UTC)
    generated_message = make_generated_message(
        message_id="m1",
        channel=make_generated_channel(channel_id="123", name="general"),
        sender="alice",
        content="hello",
        timestamp=timestamp,
    )

    result = ChatClientAdapter._to_api_message(generated_message)
    assert result.channel == "123"
    assert result.text == "hello"
