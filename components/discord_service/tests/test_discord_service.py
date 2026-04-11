"""Tests for discord_service endpoints."""
from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING
from unittest.mock import MagicMock, patch

if TYPE_CHECKING:
    from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

from chat_client_api import Channel, Message
from discord_service.main import app, get_client

client = TestClient(app)


@pytest.fixture
def mock_discord_client() -> Generator[MagicMock]:
    """Fixture to inject a mock DiscordClient into the FastAPI app."""
    mock = MagicMock()
    app.dependency_overrides[get_client] = lambda: mock
    yield mock
    app.dependency_overrides.clear()


def test_health_check() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_get_channels_success(mock_discord_client: MagicMock) -> None:
    mock_discord_client.get_channels.return_value = [
        Channel(channel_id="123", name="general")
    ]

    response = client.get("/channels")

    assert response.status_code == 200
    assert response.json()[0]["name"] == "general"
    mock_discord_client.get_channels.assert_called_once()


def test_send_message_success(mock_discord_client: MagicMock) -> None:
    channel = Channel(channel_id="123", name="general")
    expected_msg = Message(
        message_id="123:msg_01",
        channel="123",
        sender="me",
        text="Hello world",
        timestamp=datetime.now(UTC).isoformat(),
    )

    mock_discord_client.get_channels.return_value = [channel]
    mock_discord_client.send_message.return_value = expected_msg

    response = client.post("/channels/123/messages", json={"content": "Hello world"})

    assert response.status_code == 200
    assert response.json()["text"] == "Hello world"
    mock_discord_client.send_message.assert_called_once()


def test_send_message_channel_not_found(mock_discord_client: MagicMock) -> None:
    mock_discord_client.get_channels.return_value = []

    response = client.post("/channels/999/messages", json={"content": "Fail"})

    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


def test_send_message_discord_error(mock_discord_client: MagicMock) -> None:
    channel = Channel(channel_id="123", name="general")
    mock_discord_client.get_channels.return_value = [channel]
    mock_discord_client.send_message.side_effect = RuntimeError("Discord Down")

    response = client.post("/channels/123/messages", json={"content": "Hello"})

    assert response.status_code == 502
    assert "Discord API error" in response.json()["detail"]


def test_login_redirect() -> None:
    """GET /auth/login should redirect to the Discord authorization URL."""
    fake_url = "https://discord.com/api/oauth2/authorize?mocked=true"

    with patch(
        "discord_client_impl.auth.DiscordOAuthHandler.get_authorization_url",
        return_value=fake_url,
    ):
        response = client.get("/auth/login", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == fake_url


def test_callback_success() -> None:
    """GET /auth/callback should return success when given a valid code."""
    fake_code = "valid-code-123"
    fake_token = "mock-access-token-456"  # noqa: S105

    with patch(
        "discord_client_impl.auth.DiscordOAuthHandler.exchange_code",
        return_value=fake_token,
    ):
        response = client.get(f"/auth/callback?code={fake_code}")

    assert response.status_code == 200
    assert response.json() == {"message": "Authentication successful"}


def test_callback_missing_code() -> None:
    """GET /auth/callback should return 422 if code is missing."""
    response = client.get("/auth/callback")
    assert response.status_code == 422


def test_callback_exchange_error() -> None:
    """GET /auth/callback should return 400 if token exchange fails."""
    with patch(
        "discord_client_impl.auth.DiscordOAuthHandler.exchange_code",
        side_effect=RuntimeError("Invalid authorization code"),
    ):
        response = client.get("/auth/callback?code=bad-code")

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid authorization code"


def test_get_messages_success(mock_discord_client: MagicMock) -> None:
    """Test successfully fetching messages for a channel."""
    channel_id = "123"
    chan = Channel(channel_id=channel_id, name="general")
    mock_discord_client.get_channels.return_value = [chan]

    mock_messages = [
        Message(
            message_id="123:m1",
            channel="123",
            sender="user1",
            text="Hello",
            timestamp=datetime.now(UTC).isoformat(),
        )
    ]
    mock_discord_client.get_messages.return_value = mock_messages

    response = client.get(f"/channels/{channel_id}/messages?limit=5")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["text"] == "Hello"
    mock_discord_client.get_messages.assert_called_once_with(channel_id, limit=5)

def test_users_me_unauthenticated() -> None:
    """GET /users/me should return 401 when not authenticated."""
    # Use a fresh client without session cookies
    from starlette.testclient import TestClient
    fresh_client = TestClient(app, cookies={})
    response = fresh_client.get("/users/me")
    assert response.status_code == 401
    assert "Not authenticated" in response.json()["detail"]

def test_get_messages_discord_error(mock_discord_client: MagicMock) -> None:
    """GET /channels/{channel_id}/messages should return 502 on Discord error."""
    channel_id = "123"
    chan = Channel(channel_id=channel_id, name="general")
    mock_discord_client.get_channels.return_value = [chan]
    mock_discord_client.get_messages.side_effect = RuntimeError("Discord Down")

    response = client.get(f"/channels/{channel_id}/messages?limit=5")

    assert response.status_code == 502
    assert "Discord API error" in response.json()["detail"]
