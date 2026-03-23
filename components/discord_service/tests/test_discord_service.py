import pytest
from collections.abc import Generator
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from discord_service.main import app
from chat_client_api.models import Channel, Message
from datetime import datetime, UTC
from discord_service.main import get_client


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
    mock_discord_client.get_channels.return_value = [Channel(id="123", name="general")]

    response = client.get("/channels")

    assert response.status_code == 200
    assert response.json()[0]["name"] == "general"
    mock_discord_client.get_channels.assert_called_once()


def test_send_message_success(mock_discord_client: MagicMock) -> None:
    channel = Channel(id="123", name="general")
    expected_msg = Message(
        id="msg_01",
        channel=channel,
        sender="me",
        content="Hello world",
        timestamp=datetime.now(UTC),
    )

    mock_discord_client.get_channels.return_value = [channel]
    mock_discord_client.send_message.return_value = expected_msg

    response = client.post("/channels/123/messages", json={"content": "Hello world"})

    assert response.status_code == 200
    assert response.json()["content"] == "Hello world"

    mock_discord_client.send_message.assert_called_once()


def test_send_message_channel_not_found(mock_discord_client: MagicMock) -> None:
    mock_discord_client.get_channels.return_value = []

    response = client.post("/channels/999/messages", json={"content": "Fail"})

    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


def test_send_message_discord_error(mock_discord_client: MagicMock) -> None:
    channel = Channel(id="123", name="general")
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
        # follow_redirects=False allows us to inspect the 307 status code
        response = client.get("/auth/login", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == fake_url


def test_callback_success() -> None:
    """GET /auth/callback should return an access token when given a valid code."""
    fake_code = "valid-code-123"
    fake_token = "mock-access-token-456"  # noqa: S105

    with patch(
        "discord_client_impl.auth.DiscordOAuthHandler.exchange_code",
        return_value=fake_token,
    ):
        response = client.get(f"/auth/callback?code={fake_code}")

    assert response.status_code == 200
    assert response.json() == {
        "access_token": fake_token,
        "token_type": "Bearer",
    }


def test_callback_missing_code() -> None:
    """GET /auth/callback should return 422 Unprocessable Entity if code is missing."""
    response = client.get("/auth/callback")
    assert response.status_code == 422


def test_callback_exchange_error() -> None:
    """GET /auth/callback should return 400 Bad Request if the token exchange fails."""

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
    chan = Channel(id=channel_id, name="general")
    mock_discord_client.get_channels.return_value = [chan]

    mock_messages = [
        Message(
            id="m1",
            channel=chan,
            sender="user1",
            content="Hello",
            timestamp=datetime.now(UTC),
        )
    ]
    mock_discord_client.get_messages.return_value = mock_messages

    response = client.get(f"/channels/{channel_id}/messages?limit=5")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["content"] == "Hello"
    mock_discord_client.get_messages.assert_called_once_with(chan, limit=5)
