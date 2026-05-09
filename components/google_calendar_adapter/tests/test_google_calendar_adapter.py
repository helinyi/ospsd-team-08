"""Tests for google_calendar_adapter components."""
from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

import pytest

from google_calendar_adapter.event_impl import GoogleCalendarEvent
from google_calendar_adapter.impl import GoogleCalendarClient


# --- event_impl.py tests ---

def test_event_id() -> None:
    event = GoogleCalendarEvent({"id": "abc123"})
    assert event.id == "abc123"


def test_event_title() -> None:
    event = GoogleCalendarEvent({"summary": "Team Meeting"})
    assert event.title == "Team Meeting"


def test_event_title_missing() -> None:
    event = GoogleCalendarEvent({})
    assert event.title == ""


def test_event_start_time_datetime() -> None:
    event = GoogleCalendarEvent({"start": {"dateTime": "2026-05-01T09:00:00+00:00"}})
    assert event.start_time == datetime(2026, 5, 1, 9, 0, tzinfo=UTC)


def test_event_start_time_date_only() -> None:
    event = GoogleCalendarEvent({"start": {"date": "2026-05-01"}})
    assert event.start_time == datetime(2026, 5, 1, 0, 0)   # noqa: DTZ001


def test_event_start_time_missing_raises() -> None:
    event = GoogleCalendarEvent({})
    with pytest.raises(ValueError, match="Missing start time"):
        _ = event.start_time


def test_event_end_time_datetime() -> None:
    event = GoogleCalendarEvent({"end": {"dateTime": "2026-05-01T10:00:00+00:00"}})
    assert event.end_time == datetime(2026, 5, 1, 10, 0, tzinfo=UTC)


def test_event_end_time_date_only() -> None:
    event = GoogleCalendarEvent({"end": {"date": "2026-05-01"}})
    assert event.end_time == datetime(2026, 5, 1, 0, 0)  # noqa: DTZ001


def test_event_end_time_missing_raises() -> None:
    event = GoogleCalendarEvent({})
    with pytest.raises(ValueError, match="Missing end time"):
        _ = event.end_time


def test_event_location() -> None:
    event = GoogleCalendarEvent({"location": "Zoom"})
    assert event.location == "Zoom"


def test_event_location_missing() -> None:
    event = GoogleCalendarEvent({})
    assert event.location is None


def test_event_description() -> None:
    event = GoogleCalendarEvent({"description": "Weekly sync"})
    assert event.description == "Weekly sync"


def test_event_description_missing() -> None:
    event = GoogleCalendarEvent({})
    assert event.description is None


# --- client.py tests ---

def test_get_connected_calendar_client_raises_when_credentials_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("GOOGLE_OAUTH_CREDENTIALS_PATH", "/nonexistent/credentials.json")
    from google_calendar_adapter.client import get_connected_calendar_client
    with pytest.raises(RuntimeError, match="Google OAuth credentials file not found"):
        get_connected_calendar_client()


# --- __init__.py tests ---

def test_get_calendar_client_raises_when_credentials_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("GOOGLE_OAUTH_CREDENTIALS_PATH", "/nonexistent/credentials.json")
    from google_calendar_adapter import get_calendar_client
    with pytest.raises(RuntimeError, match="Google OAuth credentials file not found"):
        get_calendar_client()


# --- impl.py tests ---

def _build_mock_service() -> MagicMock:
    """Build a mock Google Calendar service."""
    return MagicMock()


def test_require_service_raises_when_not_connected() -> None:
    client = GoogleCalendarClient()
    with pytest.raises(RuntimeError, match="not connected"):
        client._require_calendar_service()


def test_get_event_returns_event() -> None:
    client = GoogleCalendarClient()
    mock_service = _build_mock_service()
    mock_service.events().get().execute.return_value = {
        "id": "evt1",
        "summary": "Meeting",
        "start": {"dateTime": "2026-05-01T09:00:00+00:00"},
        "end": {"dateTime": "2026-05-01T10:00:00+00:00"},
    }
    client._service = mock_service

    event = client.get_event("evt1")
    assert event.id == "evt1"
    assert event.title == "Meeting"


def test_get_events_yields_events() -> None:
    client = GoogleCalendarClient()
    mock_service = _build_mock_service()
    mock_service.events().list().execute.return_value = {
        "items": [
            {
                "id": "evt1",
                "summary": "Standup",
                "start": {"dateTime": "2026-05-01T09:00:00+00:00"},
                "end": {"dateTime": "2026-05-01T09:30:00+00:00"},
            }
        ],
        "nextPageToken": None,
    }
    client._service = mock_service

    start = datetime(2026, 5, 1, tzinfo=UTC)
    end = datetime(2026, 5, 2, tzinfo=UTC)
    events = list(client.get_events(start, end))

    assert len(events) == 1
    assert events[0].title == "Standup"


def test_from_raw_data_returns_event() -> None:
    import json
    client = GoogleCalendarClient()
    raw = json.dumps({
        "id": "evt1",
        "summary": "Meeting",
        "start": {"dateTime": "2026-05-01T09:00:00+00:00"},
        "end": {"dateTime": "2026-05-01T10:00:00+00:00"},
    })
    event = client.from_raw_data(raw)
    assert event.id == "evt1"


def test_connect_calls_build(monkeypatch: pytest.MonkeyPatch) -> None:
    mock_creds = MagicMock()
    mock_build = MagicMock()

    with (
        patch("google_calendar_adapter.impl.get_credentials", return_value=mock_creds),
        patch("google_calendar_adapter.impl.build", return_value=mock_build),
    ):
        client = GoogleCalendarClient(
            credentials_path="creds.json",
            token_path="token.json",    # noqa: S106
        )
        client.connect()

    assert client._service == mock_build

def test_get_credentials_raises_when_credentials_missing(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: pytest.TempPathFactory,
) -> None:
    """get_credentials raises FileNotFoundError when credentials file missing."""
    from google_calendar_adapter.auth import get_credentials
    with pytest.raises(FileNotFoundError, match="OAuth client-secrets file not found"):
        get_credentials(
            credentials_path="/nonexistent/credentials.json",
            token_path="/nonexistent/token.json",   # noqa: S106
        )


def test_get_credentials_refreshes_expired_token(tmp_path: pytest.FixtureRequest) -> None:
    """get_credentials refreshes expired credentials."""
    from google_calendar_adapter.auth import get_credentials

    mock_creds = MagicMock()
    mock_creds.valid = False
    mock_creds.expired = True
    mock_creds.refresh_token = "refresh_token"  # noqa: S105

    with (
        patch("google_calendar_adapter.auth.Credentials.from_authorized_user_file", return_value=mock_creds),
        patch("google_calendar_adapter.auth.Request"),
        patch("pathlib.Path.exists", return_value=True),
        patch("pathlib.Path.write_text"),
    ):
        result = get_credentials(
            credentials_path="credentials.json",
            token_path="token.json",    # noqa: S106
        )
    assert result == mock_creds
    mock_creds.refresh.assert_called_once()


def test_get_credentials_returns_valid_token(tmp_path: pytest.FixtureRequest) -> None:
    """get_credentials returns valid credentials from token file."""
    from google_calendar_adapter.auth import get_credentials

    mock_creds = MagicMock()
    mock_creds.valid = True

    with (
        patch("google_calendar_adapter.auth.Credentials.from_authorized_user_file", return_value=mock_creds),
        patch("pathlib.Path.exists", return_value=True),
    ):
        result = get_credentials(
            credentials_path="credentials.json",
            token_path="token.json",    # noqa: S106
        )
    assert result == mock_creds
