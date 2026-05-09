"""OAuth credential helpers for the Google Calendar adapter."""

from __future__ import annotations

import contextlib
import os
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/tasks",
]


def get_credentials(
        credentials_path: str | None = None,
        token_path: str | None = None,
) -> Credentials:
    """Load, refresh, or create OAuth credentials for Google APIs."""
    resolved_credentials = credentials_path or os.environ.get(
        "GOOGLE_OAUTH_CREDENTIALS_PATH",
        "credentials.json",
    )
    resolved_token = token_path or os.environ.get(
        "GOOGLE_OAUTH_TOKEN_PATH",
        "token.json",
    )

    creds: Credentials | None = None

    if Path(resolved_token).exists():
        creds = Credentials.from_authorized_user_file( # type: ignore[no-untyped-call]
            resolved_token,
            SCOPES,
        )

    if creds is None or not creds.valid:
        if creds is not None and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not Path(resolved_credentials).exists():
                msg = (
                    f"OAuth client-secrets file not found at '{resolved_credentials}'. "
                    "Download it from Google Cloud Console."
                )
                raise FileNotFoundError(msg)

            flow = InstalledAppFlow.from_client_secrets_file(
                resolved_credentials,
                SCOPES,
            )
            creds = flow.run_local_server(port=0)

        # Cloud Run secret mounts are read-only; the refresh_token in the
        # mounted token.json is unchanged, so the next request can refresh
        # again from in-memory creds without persistence.
        with contextlib.suppress(OSError):
            Path(resolved_token).write_text(creds.to_json())

    return creds
