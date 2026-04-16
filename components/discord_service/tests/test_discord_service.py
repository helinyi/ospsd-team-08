"""Tests for discord_service endpoints."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from calendar_client_api.client import Client as CalendarClient
from calendar_client_api.event import Event
from calendar_client_api.task import Task
from chat_client_api import Channel, Message
from discord_service.main import app, get_calendar_client, get_client, get_oauth_handler

if TYPE_CHECKING:
    from collections.abc import Generator, Iterator

client = TestClient(app)

class FakeEvent(Event):
    def __init__( # noqa: PLR0913
            self,
            event_id: str,
            title: str,
            start_time: datetime,
            end_time: datetime,
            location: str | None = None,
            description: str | None = None,
    ) -> None:
        self._id = event_id
        self._title = title
        self._start_time = start_time
        self._end_time = end_time
        self._location = location
        self._description = description

    @property
    def id(self) -> str:
        return self._id

    @property
    def title(self) -> str:
        return self._title

    @property
    def start_time(self) -> datetime:
        return self._start_time

    @property
    def end_time(self) -> datetime:
        return self._end_time

    @property
    def location(self) -> str | None:
        return self._location

    @property
    def description(self) -> str | None:
        return self._description


class FakeTask(Task):
    @property
    def id(self) -> str:
        return "task-1"

    @property
    def title(self) -> str:
        return "placeholder"

    @property
    def due_time(self) -> datetime | None:
        return None

    @property
    def is_completed(self) -> bool:
        return False

    @property
    def description(self) -> str | None:
        return None


class FakeCalendarClient(CalendarClient):
    def get_event(self, event_id: str) -> Event:
        raise NotImplementedError

    def create_event(self, event: Event) -> Event:
        raise NotImplementedError

    def update_event(self, event: Event) -> Event:
        raise NotImplementedError

    def delete_event(self, event_id: str) -> None:
        raise NotImplementedError

    def get_events(self, start_time: datetime, end_time: datetime) -> Iterator[Event]:
        yield FakeEvent(
            event_id="1",
            title="OSPSD meeting",
            start_time=start_time,
            end_time=end_time,
            location="Zoom",
            description="Team sync",
        )

    def from_raw_data(self, raw_data: str) -> Event:
        raise NotImplementedError

    def get_task(self, task_id: str) -> Task:
        raise NotImplementedError

    def create_task(self, task: Task) -> Task:
        raise NotImplementedError

    def update_task(self, task: Task) -> Task:
        raise NotImplementedError

    def delete_task(self, task_id: str) -> None:
        raise NotImplementedError

    def get_tasks(self, start_time: datetime, end_time: datetime) -> Iterator[Task]:
        if False:
            yield FakeTask()

    def mark_task_completed(self, task_id: str) -> None:
        raise NotImplementedError

class FakeOAuthHandler:
    def get_authorization_url(self) -> str:
        return "https://discord.com/api/oauth2/authorize?mocked=true"

    def exchange_code(self, code: str) -> str:
        if code == "bad-code":
            msg = "Invalid authorization code"
            raise RuntimeError(msg)
        return "mock-access-token-456"

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
    app.dependency_overrides[get_oauth_handler] = lambda: FakeOAuthHandler()

    response = client.get("/auth/login", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "https://discord.com/api/oauth2/authorize?mocked=true"

    app.dependency_overrides.pop(get_oauth_handler, None)


def test_callback_success() -> None:
    """GET /auth/callback should return success when given a valid code."""
    app.dependency_overrides[get_oauth_handler] = lambda: FakeOAuthHandler()

    response = client.get("/auth/callback?code=valid-code-123")

    assert response.status_code == 200
    assert response.json() == {"message": "Authentication successful"}

    app.dependency_overrides.pop(get_oauth_handler, None)


def test_callback_missing_code() -> None:
    """GET /auth/callback should return 422 if code is missing."""
    app.dependency_overrides[get_oauth_handler] = lambda: FakeOAuthHandler()

    response = client.get("/auth/callback")

    assert response.status_code == 422

    app.dependency_overrides.pop(get_oauth_handler, None)


def test_callback_exchange_error() -> None:
    """GET /auth/callback should return 400 if token exchange fails."""
    app.dependency_overrides[get_oauth_handler] = lambda: FakeOAuthHandler()

    response = client.get("/auth/callback?code=bad-code")

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid authorization code"

    app.dependency_overrides.pop(get_oauth_handler, None)


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


def test_get_calendar_tomorrow() -> None:
    app.dependency_overrides[get_calendar_client] = lambda: FakeCalendarClient()

    response = client.get("/calendar/tomorrow")

    assert response.status_code == 200
    assert "OSPSD meeting" in response.json()["message"]

    app.dependency_overrides.pop(get_calendar_client, None)

def test_get_calendar_tomorrow_unconfigured() -> None:
    app.dependency_overrides.pop(get_calendar_client, None)

    response = client.get("/calendar/tomorrow")

    assert response.status_code == 503
    assert "Google OAuth credentials file not found" in response.json()["detail"]
