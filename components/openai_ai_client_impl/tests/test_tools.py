"""Tests for OpenAI AI client tool definitions and handlers."""
from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Any
from unittest.mock import MagicMock

from chat_client_api import Channel, ChatClient, Message
from openai_ai_client_impl.tools import build_openai_tools, get_tool_handlers


class FakeChatClient(ChatClient):
    """Fake chat client for testing."""

    def get_channels(self) -> list[Channel]:
        return [Channel(channel_id="123", name="general", is_private=False, channel_type="group")]

    def get_channel(self, channel_id: str) -> Channel:
        return Channel(channel_id=channel_id, name="general", is_private=False, channel_type="group")

    def get_messages(self, channel_id: str, limit: int = 10, cursor: str | None = None) -> list[Message]:
        return [Message(message_id="m1", channel=channel_id, text="hello", sender="bot", timestamp=datetime.now(UTC))]

    def get_message(self, message_id: str) -> Message:
        return Message(message_id=message_id, channel="123", text="hello world", sender="alice", timestamp=datetime.now(UTC))

    def delete_message(self, message_id: str) -> None:
        return None

    def send_message(self, channel_id: str, text: str) -> Message:
        return Message(message_id="m2", channel=channel_id, text=text, sender="me", timestamp=datetime.now(UTC))


def _make_fake_calendar_client() -> Any:
    """Create a mock calendar client that implements create_event."""
    mock_client = MagicMock()
    created_event = MagicMock()
    created_event.id = "event-1"
    created_event.title = "Team Meeting"
    created_event.start_time = datetime(2026, 5, 10, 15, 0, tzinfo=UTC)
    created_event.end_time = datetime(2026, 5, 10, 16, 0, tzinfo=UTC)
    created_event.description = "Discuss HW3 progress"
    created_event.location = "Zoom"
    mock_client.create_event.return_value = created_event
    return mock_client


def test_build_openai_tools_includes_calendar_tool() -> None:
    tools = build_openai_tools()
    tool_names = {tool["function"]["name"] for tool in tools}
    assert "create_calendar_event" in tool_names
    assert "schedule_meeting_for_message" in tool_names


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
    """Test calendar event creation via AI tool."""
    calendar_client = _make_fake_calendar_client()
    handlers = get_tool_handlers(FakeChatClient(), calendar_client=calendar_client)

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


def test_create_calendar_event_tool_no_client() -> None:
    """Returns error when no calendar client is configured."""
    handlers = get_tool_handlers(FakeChatClient(), calendar_client=None)
    result = handlers["create_calendar_event"](
        title="Meeting",
        start_time="2026-05-10T15:00:00+00:00",
        end_time="2026-05-10T16:00:00+00:00",
    )
    parsed = json.loads(result)
    assert "error" in parsed


def test_schedule_meeting_for_message_tool() -> None:
    """Test scheduling a meeting from a Discord message."""
    calendar_client = _make_fake_calendar_client()
    handlers = get_tool_handlers(FakeChatClient(), calendar_client=calendar_client)

    result = handlers["schedule_meeting_for_message"](
        channel_id="123",
        message_id="m1",
        start_time="2026-05-10T15:00:00+00:00",
        end_time="2026-05-10T16:00:00+00:00",
        location="Zoom",
    )
    parsed = json.loads(result)
    assert parsed["event_id"] == "event-1"
    calendar_client.create_event.assert_called_once()


def test_schedule_meeting_for_message_no_client() -> None:
    """Returns error when no calendar client is configured."""
    handlers = get_tool_handlers(FakeChatClient(), calendar_client=None)
    result = handlers["schedule_meeting_for_message"](
        channel_id="123",
        message_id="m1",
        start_time="2026-05-10T15:00:00+00:00",
        end_time="2026-05-10T16:00:00+00:00",
    )
    parsed = json.loads(result)
    assert "error" in parsed
