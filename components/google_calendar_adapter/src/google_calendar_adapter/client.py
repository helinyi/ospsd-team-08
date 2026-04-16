"""Factory helpers for creating a connected Google Calendar client."""

from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING

from google_calendar_adapter.impl import GoogleCalendarClient

if TYPE_CHECKING:
    from calendar_client_api.client import Client


def get_connected_calendar_client() -> Client:
    """Create and connect a Google Calendar-backed client."""
    credentials_path = os.environ.get(
        "GOOGLE_OAUTH_CREDENTIALS_PATH",
        "credentials.json",
    )
    token_path = os.environ.get(
        "GOOGLE_OAUTH_TOKEN_PATH",
        "token.json",
    )
    calendar_id = os.environ.get("GOOGLE_CALENDAR_ID", "primary")

    if not Path(credentials_path).exists():
        msg = (
            f"Google OAuth credentials file not found at '{credentials_path}'. "
            "Set GOOGLE_OAUTH_CREDENTIALS_PATH or place credentials.json in the repo root."
        )
        raise RuntimeError(msg)

    client = GoogleCalendarClient(
        calendar_id=calendar_id,
        credentials_path=credentials_path,
        token_path=token_path,
    )
    client.connect()
    return client
