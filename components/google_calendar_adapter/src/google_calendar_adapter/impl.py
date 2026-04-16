"""Concrete Google Calendar client implementation for Team 5 integration."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

import calendar_client_api
from googleapiclient.discovery import build  # type: ignore[import-untyped]

from google_calendar_adapter.auth import get_credentials
from google_calendar_adapter.event_impl import GoogleCalendarEvent

if TYPE_CHECKING:
    from collections.abc import Iterator
    from datetime import datetime


_NOT_CONNECTED_MSG = "Client is not connected. Call connect() first."

class GoogleCalendarClient(calendar_client_api.Client):
    """Google Calendar-backed implementation of the shared calendar API."""

    def __init__(
            self,
            calendar_id: str = "primary",
            tasklist_id: str = "@default",
            credentials_path: str | None = None,
            token_path: str | None = None,
    ) -> None:
        """Initialize the Google Calendar client configuration."""
        super().__init__()
        self.calendar_id = calendar_id
        self.tasklist_id = tasklist_id
        self._credentials_path = credentials_path
        self._token_path = token_path
        self._service: Any | None = None
        self._tasks_service: Any | None = None

    def connect(self) -> None:
        """Authenticate and create Google Calendar service clients."""
        creds = get_credentials(
            credentials_path=self._credentials_path,
            token_path=self._token_path,
        )
        self._service = build("calendar", "v3", credentials=creds)
        self._tasks_service = build("tasks", "v1", credentials=creds)

    def _require_calendar_service(self) -> Any: # noqa: ANN401
        """Return the connected calendar service or raise if not connected."""
        if not self._service:
            raise RuntimeError(_NOT_CONNECTED_MSG)
        return self._service

    def get_event(self, event_id: str) -> calendar_client_api.Event:
        """Fetch a single event by its ID."""
        svc = self._require_calendar_service()
        response = svc.events().get(
            calendarId=self.calendar_id,
            eventId=event_id,
        ).execute()
        return GoogleCalendarEvent(response)

    def create_event(
            self,
            event: calendar_client_api.Event,
    ) -> calendar_client_api.Event:
        """Create a new calendar event."""
        raise NotImplementedError

    def update_event(
            self,
            event: calendar_client_api.Event,
    ) -> calendar_client_api.Event:
        """Update an existing calendar event."""
        raise NotImplementedError

    def delete_event(self, event_id: str) -> None:
        """Delete a calendar event by its ID."""
        raise NotImplementedError

    def get_events(
            self,
            start_time: datetime,
            end_time: datetime,
    ) -> Iterator[calendar_client_api.Event]:
        """Yield events within the given time range."""
        svc = self._require_calendar_service()
        page_token = None

        while True:
            events_result = svc.events().list(
                calendarId=self.calendar_id,
                timeMin=start_time.isoformat(),
                timeMax=end_time.isoformat(),
                singleEvents=True,
                orderBy="startTime",
                pageToken=page_token,
            ).execute()

            for event in events_result.get("items", []):
                yield GoogleCalendarEvent(event)

            page_token = events_result.get("nextPageToken")
            if not page_token:
                break

    def from_raw_data(self, raw_data: str) -> calendar_client_api.Event:
        """Build an event object from raw JSON data."""
        data = json.loads(raw_data)
        return GoogleCalendarEvent(data)

    def get_task(self, task_id: str) -> calendar_client_api.Task:
        """Fetch a single task by its ID."""
        raise NotImplementedError

    def create_task(self, task: calendar_client_api.Task) -> calendar_client_api.Task:
        """Create a new task."""
        raise NotImplementedError

    def update_task(self, task: calendar_client_api.Task) -> calendar_client_api.Task:
        """Update an existing task."""
        raise NotImplementedError

    def delete_task(self, task_id: str) -> None:
        """Delete a task by its ID."""
        raise NotImplementedError

    def get_tasks(
            self,
            _start_time: datetime,
            _end_time: datetime,
    ) -> Iterator[calendar_client_api.Task]:
        """Return tasks in a time range."""
        if False:
            yield
        return

    def mark_task_completed(self, task_id: str) -> None:
        """Mark a task as completed."""
        raise NotImplementedError
