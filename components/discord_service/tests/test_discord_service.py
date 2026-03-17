import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from discord_service.main import app
from chat_client_api.models import Channel, Message
from datetime import datetime, UTC

client = TestClient(app)


@pytest.fixture
def mock_discord_client():
    """Create a mock instance of the DiscordClient."""
    with patch("discord_service.main.get_client") as mock_get:
        mock_instance = MagicMock()
        mock_get.return_value = mock_instance
        yield mock_instance


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_get_channels_success(mock_discord_client):
    mock_discord_client.get_channels.return_value = [Channel(id="123", name="general")]

    response = client.get("/channels")

    assert response.status_code == 200
    assert response.json()[0]["name"] == "general"
    mock_discord_client.get_channels.assert_called_once()


def test_send_message_success(mock_discord_client):
    channel = Channel(id="123", name="general")
    mock_discord_client.get_channels.return_value = [channel]

    expected_msg = Message(
        id="msg_01",
        channel=channel,
        sender="me",
        content="Hello world",
        timestamp=datetime.now(UTC),
    )
    mock_discord_client.send_message.return_value = expected_msg

    response = client.post("/channels/123/messages", json={"content": "Hello world"})

    assert response.status_code == 200
    assert response.json()["content"] == "Hello world"
    mock_discord_client.send_message.assert_called_once()


def test_send_message_channel_not_found(mock_discord_client):
    mock_discord_client.get_channels.return_value = []

    response = client.post("/channels/999/messages", json={"content": "Fail"})

    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


def test_send_message_discord_error(mock_discord_client):
    channel = Channel(id="123", name="general")
    mock_discord_client.get_channels.return_value = [channel]
    mock_discord_client.send_message.side_effect = RuntimeError("Discord Down")

    response = client.post("/channels/123/messages", json={"content": "Hello"})

    assert response.status_code == 502
    assert "Discord API error" in response.json()["detail"]
