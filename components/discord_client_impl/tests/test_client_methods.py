"""Unit tests for discord_client_impl."""
# components/discord_client_impl/tests/test_client_methods.py

from __future__ import annotations

from datetime import UTC
from unittest.mock import MagicMock, patch

import pytest
import requests

from chat_client_api.models import Channel, Message
from discord_client_impl.client import DiscordClient

@pytest.fixture
def mock_auth() -> MagicMock:
    """Create a mock authenticator."""
    auth = MagicMock()
    auth.get_headers.return_value = {
        "Authorization": "Bot test-token",
        "Content-Type": "application/json",
    }
    return auth


@pytest.fixture
def client(mock_auth: MagicMock, monkeypatch: pytest.MonkeyPatch) -> DiscordClient:
    """Create a DiscordClient with mocked auth and guild ID."""
    monkeypatch.setenv("DISCORD_GUILD_ID", "123456789")
    return DiscordClient(authenticator=mock_auth)


def test_get_channels_returns_text_channels_only(
    client: DiscordClient,
) -> None:
    """Only type=0 (text) channels are returned."""
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.json.return_value = [
        {"id": "111", "name": "general", "type": 0},
        {"id": "222", "name": "voice-chat", "type": 2},  # voice, should be filtered
        {"id": "333", "name": "announcements", "type": 0},
    ]

    with patch("discord_client_impl.client.requests.get", return_value=mock_response):
        channels = client.get_channels()

    assert len(channels) == 2
    assert all(isinstance(c, Channel) for c in channels)
    assert channels[0].id == "111"
    assert channels[1].id == "333"


def test_get_channels_raises_on_api_error(
    client: DiscordClient,
) -> None:
    """RuntimeError is raised when Discord API returns non-200."""
    mock_response = MagicMock()
    mock_response.ok = False
    mock_response.status_code = 403

    with (
        patch("discord_client_impl.client.requests.get", return_value=mock_response),
        pytest.raises(RuntimeError, match="403"),
    ):
        client.get_channels()


def test_get_messages_returns_oldest_first(
    client: DiscordClient,
) -> None:
    """Messages are returned oldest first (Discord returns newest first)."""
    channel = Channel(id="111", name="general")
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.json.return_value = [
        {
            "id": "999",
            "content": "newest",
            "author": {"username": "user1"},
            "timestamp": "2024-01-01T00:00:02+00:00",
        },
        {
            "id": "998",
            "content": "oldest",
            "author": {"username": "user1"},
            "timestamp": "2024-01-01T00:00:01+00:00",
        },
    ]

    with patch("discord_client_impl.client.requests.get", return_value=mock_response):
        messages = client.get_messages(channel, limit=2)

    assert len(messages) == 2
    assert messages[0].content == "oldest"
    assert messages[1].content == "newest"


def test_get_messages_returns_message_objects(
    client: DiscordClient,
) -> None:
    """get_messages returns proper Message objects with correct fields."""
    channel = Channel(id="111", name="general")
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.json.return_value = [
        {
            "id": "999",
            "content": "hello",
            "author": {"username": "testuser"},
            "timestamp": "2024-01-01T00:00:01+00:00",
        },
    ]

    with patch("discord_client_impl.client.requests.get", return_value=mock_response):
        messages = client.get_messages(channel)

    assert len(messages) == 1
    msg = messages[0]
    assert isinstance(msg, Message)
    assert msg.id == "999"
    assert msg.content == "hello"
    assert msg.sender == "testuser"
    assert msg.channel == channel
    assert msg.timestamp.tzinfo == UTC


def test_get_messages_raises_on_api_error(
    client: DiscordClient,
) -> None:
    """RuntimeError is raised when Discord API returns non-200."""
    channel = Channel(id="111", name="general")
    mock_response = MagicMock()
    mock_response.ok = False
    mock_response.status_code = 403

    with (
        patch("discord_client_impl.client.requests.get", return_value=mock_response),
        pytest.raises(RuntimeError, match="403"),
    ):
        client.get_messages(channel)



def test_send_message_returns_message_object(
    client: DiscordClient,
) -> None:
    """send_message returns a proper Message object."""
    channel = Channel(id="111", name="general")
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.json.return_value = {
        "id": "777",
        "content": "hello world",
        "author": {"username": "me"},
        "timestamp": "2024-01-01T00:00:01+00:00",
    }

    with patch("discord_client_impl.client.requests.post", return_value=mock_response):
        msg = client.send_message(channel, "hello world")

    assert isinstance(msg, Message)
    assert msg.id == "777"
    assert msg.content == "hello world"
    assert msg.sender == "me"
    assert msg.channel == channel


def test_send_message_raises_on_api_error(
    client: DiscordClient,
) -> None:
    """RuntimeError is raised when Discord API returns non-200."""
    channel = Channel(id="111", name="general")
    mock_response = MagicMock()
    mock_response.ok = False
    mock_response.status_code = 403

    with (
        patch("discord_client_impl.client.requests.post", return_value=mock_response),
        pytest.raises(RuntimeError, match="403"),
    ):
        client.send_message(channel, "hi")


def test_client_raises_without_guild_id(
    mock_auth: MagicMock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """RuntimeError is raised if DISCORD_GUILD_ID is not set."""
    monkeypatch.delenv("DISCORD_GUILD_ID", raising=False)
    with pytest.raises(RuntimeError, match="DISCORD_GUILD_ID"):
        DiscordClient(authenticator=mock_auth)


def test_get_channels_raises_on_network_error(
    client: DiscordClient,
) -> None:
    """RuntimeError is raised when a network error occurs fetching channels."""
    with (
        patch(
            "discord_client_impl.client.requests.get",
            side_effect=requests.RequestException("network error"),
        ),
        pytest.raises(RuntimeError, match="network error"),
    ):
        client.get_channels()


def test_get_messages_raises_on_network_error(
    client: DiscordClient,
) -> None:
    """RuntimeError is raised when a network error occurs fetching messages."""
    channel = Channel(id="111", name="general")
    with (
        patch(
            "discord_client_impl.client.requests.get",
            side_effect=requests.RequestException("network error"),
        ),
        pytest.raises(RuntimeError, match="network error"),
    ):
        client.get_messages(channel)


def test_send_message_raises_on_network_error(
    client: DiscordClient,
) -> None:
    """RuntimeError is raised when a network error occurs sending a message."""
    channel = Channel(id="111", name="general")
    with (
        patch(
            "discord_client_impl.client.requests.post",
            side_effect=requests.RequestException("network error"),
        ),
        pytest.raises(RuntimeError, match="network error"),
    ):
        client.send_message(channel, "hi")
