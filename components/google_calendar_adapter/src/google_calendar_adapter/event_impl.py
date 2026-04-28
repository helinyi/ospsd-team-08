"""Event wrapper for Google Calendar API responses."""

from __future__ import annotations

from datetime import datetime

from calendar_client_api.event import Event


class GoogleCalendarEvent(Event):
    """Concrete event wrapper around raw Google Calendar event data."""

    def __init__(self, raw: dict[str, object]) -> None:
        """Store the raw Google Calendar event payload."""
        self._raw = raw

    @property
    def id(self) -> str:
        """Return the event identifier."""
        return str(self._raw.get("id", ""))

    @property
    def title(self) -> str:
        """Return the event title."""
        return str(self._raw.get("summary", ""))

    @property
    def start_time(self) -> datetime:
        """Return the event start time."""
        start = self._raw.get("start", {})
        if isinstance(start, dict) and "dateTime" in start:
            return datetime.fromisoformat(str(start["dateTime"]))
        if isinstance(start, dict) and "date" in start:
            return datetime.fromisoformat(f"{start['date']}T00:00:00")
        msg = "Missing start time"
        raise ValueError(msg)

    @property
    def end_time(self) -> datetime:
        """Return the event end time."""
        end = self._raw.get("end", {})
        if isinstance(end, dict) and "dateTime" in end:
            return datetime.fromisoformat(str(end["dateTime"]))
        if isinstance(end, dict) and "date" in end:
            return datetime.fromisoformat(f"{end['date']}T00:00:00")
        msg = "Missing end time"
        raise ValueError(msg)

    @property
    def location(self) -> str | None:
        """Return the event location, if present."""
        value = self._raw.get("location")
        return None if value is None else str(value)

    @property
    def description(self) -> str | None:
        """Return the event description, if present."""
        value = self._raw.get("description")
        return None if value is None else str(value)
