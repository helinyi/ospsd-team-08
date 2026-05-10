"""Service helpers for formatting calendar data for chat responses."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING

if TYPE_CHECKING:   # pragma: no cover
    from collections.abc import Iterable

    from calendar_client_api import Event
    from calendar_client_api.client import Client


def get_tomorrow_time_range(now: datetime, days: int = 1) -> tuple[datetime, datetime]:
    """Return the start and end of a future day (default: tomorrow)."""
    future = now.astimezone(UTC).date() + timedelta(days=days)
    start = datetime.combine(future, datetime.min.time(), tzinfo=UTC)
    end = start + timedelta(days=1)
    return start, end


def format_events(events: Iterable[Event]) -> str:
    """Format calendar events into a readable message for chat."""
    event_list = list(events)
    if not event_list:
        return "No events found."

    lines = [
        f"- {event.title} | {event.start_time} to {event.end_time}"
        for event in event_list
    ]
    return "\n".join(lines)


def get_events_message(
        calendar_client: Client,
        start_time: datetime,
        end_time: datetime,
) -> str:
    """Fetch events from the calendar API and format them for chat."""
    events = calendar_client.list_events(start_time, end_time)
    return format_events(events)


def get_tomorrows_events_message(
        calendar_client: Client,
        now: datetime,
) -> str:
    """Fetch and format tomorrow's events for chat."""
    start_time, end_time = get_tomorrow_time_range(now)
    return get_events_message(calendar_client, start_time, end_time)
