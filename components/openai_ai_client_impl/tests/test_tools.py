from __future__ import annotations

import json
from datetime import UTC, datetime

from chat_client_api import Channel, ChatClient, Message
from openai_ai_client_impl.tools import build_openai_tools, get_tool_handlers


class FakeChatClient(ChatClient):
    def get_channels(self) -> list[Channel]:
        return [
            Channel(
                channel_id="123",
                name="general",
                is_private=False,
                channel_type="group",
            )
        ]

    def get_channel(self, channel_id: str) -> Channel:
        return Channel(
            channel_id=channel_id,
            name="general",
            is_private=False,
            channel_type="group",
        )

    def get_messages(
        self,
        channel_id: str,
        limit: int = 10,
        cursor: str | None = None,
    ) -> list[Message]:
        return [
            Message(
                message_id="m1",
                channel=channel_id,
                text="hello",
                sender="bot",
                timestamp=datetime.now(UTC),
            )
        ]

    def get_message(self, message_id: str) -> Message:
        return Message(
            message_id=message_id,
            channel="123",
            text="hello",
            sender="bot",
            timestamp=datetime.now(UTC),
        )

    def delete_message(self, message_id: str) -> None:
        return None

    def send_message(self, channel_id: str, text: str) -> Message:
        return Message(
            message_id="m2",
            channel=channel_id,
            text=text,
            sender="me",
            timestamp=datetime.now(UTC),
        )


class FakeCalendarRequest:
    def __init__(self, response: dict[str, object]) -> None:
        self._response = response

    def execute(self) -> dict[str, object]:
        return self._response


class FakeCalendarEvents:
    def __init__(self) -> None:
        self.last_calendar_id: str | None = None
        self.last_body: dict[str, object] | None = None

    def insert( # type: ignore[no-untyped-def]
        self,
        **kwargs: object,
    ) -> FakeCalendarRequest:
        calendar_id = str(kwargs["calendarId"])
        body = kwargs["body"]
        assert isinstance(body, dict)

        self.last_calendar_id = calendar_id
        self.last_body = body

        return FakeCalendarRequest(
            {
                "id": "event-1",
                "summary": body["summary"],
                "start": body["start"],
                "end": body["end"],
                "description": body.get("description"),
                "location": body.get("location"),
            }
        )

def insert( # type: ignore[no-untyped-def]
    self,
    **kwargs: object,
) -> FakeCalendarRequest:
    calendar_id = str(kwargs["calendarId"])
    body = kwargs["body"]
    assert isinstance(body, dict)

    self.last_calendar_id = calendar_id
    self.last_body = body

    return FakeCalendarRequest(
        {
            "id": "event-1",
            "summary": body["summary"],
            "start": body["start"],
            "end": body["end"],
            "description": body.get("description"),
            "location": body.get("location"),
        }
    )

class FakeCalendarService:
    def __init__(self) -> None:
        self.events_resource = FakeCalendarEvents()

    def events(self) -> FakeCalendarEvents:
        return self.events_resource


class FakeCalendarClient:
    def __init__(self) -> None:
        self.calendar_id = "primary"
        self.service = FakeCalendarService()

    def _require_calendar_service(self) -> FakeCalendarService:
        return self.service


def test_build_openai_tools_includes_calendar_tool() -> None:
    tools = build_openai_tools()
    tool_names = {tool["function"]["name"] for tool in tools}

    assert "create_calendar_event" in tool_names


def test_get_channels_tool() -> None:
    handlers = get_tool_handlers(FakeChatClient())
    result = handlers["get_channels"]()
    parsed = json.loads(result)

    assert len(parsed) == 1
    assert parsed[0]["channel_id"] == "123"
    assert parsed[0]["name"] == "general"


def test_send_message_tool() -> None:
    handlers = get_tool_handlers(FakeChatClient())
    result = handlers["send_message"](channel_id="123", text="hi")
    parsed = json.loads(result)

    assert parsed["channel"] == "123"
    assert parsed["text"] == "hi"


def test_get_channel_tool() -> None:
    handlers = get_tool_handlers(FakeChatClient())
    result = handlers["get_channel"](channel_id="123")
    parsed = json.loads(result)

    assert parsed["channel_id"] == "123"
    assert parsed["name"] == "general"


def test_get_messages_tool() -> None:
    handlers = get_tool_handlers(FakeChatClient())
    result = handlers["get_messages"](channel_id="123", limit=5)
    parsed = json.loads(result)

    assert len(parsed) == 1
    assert parsed[0]["text"] == "hello"


def test_create_calendar_event_tool() -> None:
    calendar_client = FakeCalendarClient()
    handlers = get_tool_handlers(
        FakeChatClient(),
        calendar_client=calendar_client,
    )

    result = handlers["create_calendar_event"](
        title="Team Meeting",
        start_time="2026-05-10T15:00:00+00:00",
        end_time="2026-05-10T16:00:00+00:00",
        description="Discuss HW3 progress",
        location="Zoom",
    )
    parsed = json.loads(result)

    assert parsed["event_id"] == "event-1"
    assert parsed["title"] == "Team Meeting"
    assert parsed["start_time"] == "2026-05-10T15:00:00+00:00"
    assert parsed["end_time"] == "2026-05-10T16:00:00+00:00"
    assert parsed["description"] == "Discuss HW3 progress"
    assert parsed["location"] == "Zoom"

    body = calendar_client.service.events_resource.last_body
    assert body is not None
    assert body["summary"] == "Team Meeting"
