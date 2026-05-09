"""Google Calendar adapter — registers itself via a simple factory registry."""
from __future__ import annotations

from typing import TYPE_CHECKING

from google_calendar_adapter.client import get_connected_calendar_client

if TYPE_CHECKING:
    from calendar_client_api import Client


def get_calendar_client() -> Client:
    """Return a Google Calendar client instance."""
    return get_connected_calendar_client()
