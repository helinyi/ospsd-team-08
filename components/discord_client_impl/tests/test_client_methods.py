"""Unit tests for discord_client_impl."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
import requests

from chat_client_api import Channel, Message
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


def test_get_channels_returns_text_channels_only(client: DiscordClient) -> None:
    """Only type=0 (text) channels are returned."""
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.json.return_value = [
        {"id": "111", "name": "general", "type": 0},
        {"id": "222", "name": "voice-chat", "type": 2},
        {"id": "333", "name": "announcements", "type": 0},
    ]

    with patch("discord_client_impl.client.requests.get", return_value=mock_response):
        channels = client.get_channels()

    assert len(channels) == 2
    assert all(isinstance(c, Channel) for c in channels)
    assert channels[0].channel_id == "111"
    assert channels[1].channel_id == "333"


def test_get_channels_raises_on_api_error(client: DiscordClient) -> None:
    """RuntimeError is raised when Discord API returns non-200."""
    mock_response = MagicMock()
    mock_response.ok = False
    mock_response.status_code = 403

    with (
        patch("discord_client_impl.client.requests.get", return_value=mock_response),
        pytest.raises(RuntimeError, match="403"),
    ):
        client.get_channels()


def test_get_channels_raises_on_network_error(client: DiscordClient) -> None:
    """RuntimeError is raised when a network error occurs fetching channels."""
    with (
        patch(
            "discord_client_impl.client.requests.get",
            side_effect=requests.RequestException("network error"),
        ),
        pytest.raises(RuntimeError, match="network error"),
    ):
        client.get_channels()


def test_get_channel_returns_channel(client: DiscordClient) -> None:
    """get_channel returns a Channel object."""
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.status_code = 200
    mock_response.json.return_value = {"id": "111", "name": "general"}

    with patch("discord_client_impl.client.requests.get", return_value=mock_response):
        channel = client.get_channel("111")

    assert isinstance(channel, Channel)
    assert channel.channel_id == "111"
    assert channel.name == "general"


def test_get_channel_raises_on_404(client: DiscordClient) -> None:
    """ValueError is raised when channel is not found."""
    mock_response = MagicMock()
    mock_response.ok = False
    mock_response.status_code = 404

    with (
        patch("discord_client_impl.client.requests.get", return_value=mock_response),
        pytest.raises(ValueError, match="does not exist"),
    ):
        client.get_channel("nope")


def test_get_messages_returns_oldest_first(client: DiscordClient) -> None:
    """Messages are returned oldest first."""
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
        messages = client.get_messages("111", limit=2)

    assert len(messages) == 2
    assert messages[0].text == "oldest"
    assert messages[1].text == "newest"


def test_get_messages_returns_message_objects(client: DiscordClient) -> None:
    """get_messages returns proper Message objects with correct fields."""
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
        messages = client.get_messages("111")

    assert len(messages) == 1
    msg = messages[0]
    assert isinstance(msg, Message)
    assert msg.message_id == "111:999"
    assert msg.text == "hello"
    assert msg.sender == "testuser"
    assert msg.channel == "111"


def test_get_messages_raises_on_api_error(client: DiscordClient) -> None:
    """RuntimeError is raised when Discord API returns non-200."""
    mock_response = MagicMock()
    mock_response.ok = False
    mock_response.status_code = 403

    with (
        patch("discord_client_impl.client.requests.get", return_value=mock_response),
        pytest.raises(RuntimeError, match="403"),
    ):
        client.get_messages("111")


def test_get_messages_raises_on_network_error(client: DiscordClient) -> None:
    """RuntimeError is raised when a network error occurs fetching messages."""
    with (
        patch(
            "discord_client_impl.client.requests.get",
            side_effect=requests.RequestException("network error"),
        ),
        pytest.raises(RuntimeError, match="network error"),
    ):
        client.get_messages("111")


def test_get_message_returns_message(client: DiscordClient) -> None:
    """get_message returns a Message object."""
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "id": "999",
        "content": "hello",
        "author": {"username": "testuser"},
        "timestamp": "2024-01-01T00:00:01+00:00",
    }

    with patch("discord_client_impl.client.requests.get", return_value=mock_response):
        msg = client.get_message("111:999")

    assert isinstance(msg, Message)
    assert msg.message_id == "111:999"
    assert msg.text == "hello"


def test_get_message_raises_on_invalid_format(client: DiscordClient) -> None:
    """ValueError is raised when message_id format is invalid."""
    with pytest.raises(ValueError, match="Invalid message_id format"):
        client.get_message("invalid-no-colon")


def test_get_message_raises_on_404(client: DiscordClient) -> None:
    """ValueError is raised when message is not found."""
    mock_response = MagicMock()
    mock_response.ok = False
    mock_response.status_code = 404

    with (
        patch("discord_client_impl.client.requests.get", return_value=mock_response),
        pytest.raises(ValueError, match="does not exist"),
    ):
        client.get_message("111:999")


def test_send_message_returns_message_object(client: DiscordClient) -> None:
    """send_message returns a proper Message object."""
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.json.return_value = {
        "id": "777",
        "content": "hello world",
        "author": {"username": "me"},
        "timestamp": "2024-01-01T00:00:01+00:00",
    }

    with patch("discord_client_impl.client.requests.post", return_value=mock_response):
        msg = client.send_message("111", "hello world")

    assert isinstance(msg, Message)
    assert msg.message_id == "111:777"
    assert msg.text == "hello world"
    assert msg.sender == "me"
    assert msg.channel == "111"


def test_send_message_raises_on_api_error(client: DiscordClient) -> None:
    """RuntimeError is raised when Discord API returns non-200."""
    mock_response = MagicMock()
    mock_response.ok = False
    mock_response.status_code = 403

    with (
        patch("discord_client_impl.client.requests.post", return_value=mock_response),
        pytest.raises(RuntimeError, match="403"),
    ):
        client.send_message("111", "hi")


def test_send_message_raises_on_network_error(client: DiscordClient) -> None:
    """RuntimeError is raised when a network error occurs sending a message."""
    with (
        patch(
            "discord_client_impl.client.requests.post",
            side_effect=requests.RequestException("network error"),
        ),
        pytest.raises(RuntimeError, match="network error"),
    ):
        client.send_message("111", "hi")


def test_delete_message_succeeds(client: DiscordClient) -> None:
    """delete_message succeeds when Discord API returns 204."""
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.status_code = 204

    with patch("discord_client_impl.client.requests.delete", return_value=mock_response):
        client.delete_message("111:777")


def test_delete_message_raises_on_404(client: DiscordClient) -> None:
    """ValueError is raised when message to delete is not found."""
    mock_response = MagicMock()
    mock_response.ok = False
    mock_response.status_code = 404

    with (
        patch("discord_client_impl.client.requests.delete", return_value=mock_response),
        pytest.raises(ValueError, match="does not exist"),
    ):
        client.delete_message("111:777")


def test_delete_message_raises_on_invalid_format(client: DiscordClient) -> None:
    """ValueError is raised when message_id format is invalid."""
    with pytest.raises(ValueError, match="Invalid message_id format"):
        client.delete_message("invalid-no-colon")


def test_delete_message_raises_on_network_error(client: DiscordClient) -> None:
    """RuntimeError is raised when a network error occurs deleting a message."""
    with (
        patch(
            "discord_client_impl.client.requests.delete",
            side_effect=requests.RequestException("network error"),
        ),
        pytest.raises(RuntimeError, match="network error"),
    ):
        client.delete_message("111:777")


def test_client_raises_without_guild_id(
    mock_auth: MagicMock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """RuntimeError is raised if DISCORD_GUILD_ID is not set."""
    monkeypatch.delenv("DISCORD_GUILD_ID", raising=False)
    with pytest.raises(RuntimeError, match="DISCORD_GUILD_ID"):
        DiscordClient(authenticator=mock_auth)


def test_client_uses_oauth_token_when_provided(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """DiscordClient uses OAuth headers when access_token is provided."""
    monkeypatch.setenv("DISCORD_GUILD_ID", "123456789")
    client = DiscordClient(access_token="test-oauth-token")  # noqa: S106
    assert client._headers["Authorization"] == "Bearer test-oauth-token"

def test_get_channel_raises_on_network_error(client: DiscordClient) -> None:
    """RuntimeError is raised when a network error occurs fetching channel."""
    with (
        patch(
            "discord_client_impl.client.requests.get",
            side_effect=requests.RequestException("network error"),
        ),
        pytest.raises(RuntimeError, match="network error"),
    ):
        client.get_channel("111")

def test_get_message_raises_on_network_error(client: DiscordClient) -> None:
    """RuntimeError is raised when a network error occurs fetching message."""
    with (
        patch(
            "discord_client_impl.client.requests.get",
            side_effect=requests.RequestException("network error"),
        ),
        pytest.raises(RuntimeError, match="network error"),
    ):
        client.get_message("111:999")


def test_delete_message_raises_on_api_error(client: DiscordClient) -> None:
    """RuntimeError is raised when Discord API returns non-200 deleting message."""
    mock_response = MagicMock()
    mock_response.ok = False
    mock_response.status_code = 403

    with (
        patch("discord_client_impl.client.requests.delete", return_value=mock_response),
        pytest.raises(RuntimeError, match="403"),
    ):
        client.delete_message("111:777")
