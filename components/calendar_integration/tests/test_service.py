from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from calendar_client_api.client import Client
from calendar_client_api.event import Event
from calendar_client_api.task import Task

from calendar_integration.service import (
    get_events_message,
    get_tomorrows_events_message,
)

if TYPE_CHECKING:
    from collections.abc import Iterator


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


class FakeCalendarClient(Client):
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

class EmptyCalendarClient(Client):
    def get_event(self, event_id: str) -> Event:
        raise NotImplementedError

    def create_event(self, event: Event) -> Event:
        raise NotImplementedError

    def update_event(self, event: Event) -> Event:
        raise NotImplementedError

    def delete_event(self, event_id: str) -> None:
        raise NotImplementedError

    def get_events(self, start_time: datetime, end_time: datetime) -> Iterator[Event]:
        if False:
            yield FakeEvent(
                event_id="0",
                title="unused",
                start_time=start_time,
                end_time=end_time,
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


def test_get_events_message_no_events() -> None:
    start = datetime(2026, 4, 17, 9, 0, tzinfo=UTC)
    end = datetime(2026, 4, 17, 10, 0, tzinfo=UTC)

    message = get_events_message(EmptyCalendarClient(), start, end)

    assert message == "No events found."


def test_get_events_message() -> None:
    start = datetime(2026, 4, 17, 9, 0, tzinfo=UTC)
    end = datetime(2026, 4, 17, 10, 0, tzinfo=UTC)

    message = get_events_message(FakeCalendarClient(), start, end)

    assert "OSPSD meeting" in message
    assert "2026-04-17 09:00:00" in message

def test_get_tomorrows_events_message() -> None:
    now = datetime(2026, 4, 17, 15, 30, tzinfo=UTC)

    message = get_tomorrows_events_message(FakeCalendarClient(), now)

    assert "OSPSD meeting" in message
    assert "2026-04-18 00:00:00" in message
