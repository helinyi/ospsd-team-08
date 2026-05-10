"""Adapt Google Calendar API event payloads to the shared Event dataclass."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from ospsd_calendar_api import Event


def _parse_datetime(node: object) -> datetime:
    """Parse a Google Calendar start/end node into a tz-aware datetime."""
    if not isinstance(node, dict):
        msg = "Event start/end must be a dict"
        raise TypeError(msg)
    if "dateTime" in node:
        return datetime.fromisoformat(str(node["dateTime"]))
    if "date" in node:
        return datetime.fromisoformat(f"{node['date']}T00:00:00").replace(tzinfo=UTC)
    msg = "Event start/end has neither 'dateTime' nor 'date'"
    raise ValueError(msg)


def event_from_google(raw: dict[str, Any]) -> Event:
    """Convert a Google Calendar API event payload into a shared Event."""
    description = raw.get("description")
    location = raw.get("location")
    return Event(
        id=str(raw.get("id", "")),
        title=str(raw.get("summary", "")),
        start_time=_parse_datetime(raw.get("start")),
        end_time=_parse_datetime(raw.get("end")),
        description=str(description) if description is not None else None,
        location=str(location) if location is not None else None,
    )
