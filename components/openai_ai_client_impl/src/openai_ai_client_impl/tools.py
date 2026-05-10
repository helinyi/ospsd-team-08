"""Tool definitions and handlers for the OpenAI AI client."""

from __future__ import annotations

import json
from datetime import datetime
from typing import TYPE_CHECKING, Any, cast

from pydantic import BaseModel, Field

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import Callable

    from calendar_client_api import Client as CalendarClient
    from chat_client_api import Channel, ChatClient, Message


# --- Pydantic models for typed tool schemas ---

class GetChannelArgs(BaseModel):
    """Arguments for get_channel tool."""

    channel_id: str = Field(description="The target channel ID.")


class GetMessagesArgs(BaseModel):
    """Arguments for get_messages tool."""

    channel_id: str = Field(description="The target channel ID.")
    limit: int = Field(default=10, description="Maximum number of messages to return.")
    cursor: str | None = Field(default=None, description="Optional pagination cursor.")


class SendMessageArgs(BaseModel):
    """Arguments for send_message tool."""

    channel_id: str = Field(description="The target channel ID.")
    text: str = Field(description="The message content to send.")


class CreateCalendarEventArgs(BaseModel):
    """Arguments for create_calendar_event tool."""

    title: str = Field(description="The event title.")
    start_time: str = Field(description="Event start time as ISO datetime string e.g. 2026-05-10T15:00:00+00:00.")
    end_time: str = Field(description="Event end time as ISO datetime string e.g. 2026-05-10T16:00:00+00:00.")
    description: str | None = Field(default=None, description="Optional event description.")
    location: str | None = Field(default=None, description="Optional event location.")


class ScheduleMeetingArgs(BaseModel):
    """Arguments for schedule_meeting_for_message tool."""

    channel_id: str = Field(description="The Discord channel ID to fetch the message from.")
    message_id: str = Field(description="The message ID to use as meeting context.")
    start_time: str = Field(description="Meeting start time as ISO datetime string.")
    end_time: str = Field(description="Meeting end time as ISO datetime string.")
    location: str | None = Field(default=None, description="Optional meeting location.")


def build_openai_tools() -> list[dict[str, Any]]:
    """Return OpenAI tool definitions for the shared chat and calendar APIs."""
    return [
        {
            "type": "function",
            "function": {
                "name": "get_channels",
                "description": "List all available chat channels or conversations.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": [],
                    "additionalProperties": False,
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_channel",
                "description": "Get details for a specific channel by channel_id.",
                "parameters": GetChannelArgs.model_json_schema(),
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_messages",
                "description": "Get recent messages from a channel.",
                "parameters": GetMessagesArgs.model_json_schema(),
            },
        },
        {
            "type": "function",
            "function": {
                "name": "send_message",
                "description": "Send a message to a channel.",
                "parameters": SendMessageArgs.model_json_schema(),
            },
        },
        {
            "type": "function",
            "function": {
                "name": "create_calendar_event",
                "description": "Create a Google Calendar event.",
                "parameters": CreateCalendarEventArgs.model_json_schema(),
            },
        },
        {
            "type": "function",
            "function": {
                "name": "schedule_meeting_for_message",
                "description": (
                    "Fetch a Discord message and schedule a Google Calendar meeting "
                    "using the message content as the meeting description. "
                    "This bridges the chat and calendar verticals."
                ),
                "parameters": ScheduleMeetingArgs.model_json_schema(),
            },
        },
    ]


def _serialize_channel(channel: Channel) -> dict[str, Any]:
    """Serialize a shared API channel."""
    return {
        "channel_id": channel.channel_id,
        "name": channel.name,
        "is_private": channel.is_private,
        "channel_type": channel.channel_type,
    }


def _serialize_message(message: Message) -> dict[str, Any]:
    """Serialize a shared API message."""
    return {
        "message_id": message.message_id,
        "channel": message.channel,
        "text": message.text,
        "sender": message.sender,
        "timestamp": message.timestamp.isoformat(),
    }

def _serialize_created_event(created: Any) -> str:  # noqa: ANN401
    """Serialize a created calendar event to JSON."""
    return json.dumps({
        "event_id": getattr(created, "id", ""),
        "title": getattr(created, "title", ""),
        "start_time": created.start_time.isoformat(),
        "end_time": created.end_time.isoformat(),
        "location": getattr(created, "location", None),
        "description": getattr(created, "description", None),
    })


def get_tool_handlers(
    chat_client: ChatClient,
    calendar_client: CalendarClient | None = None,
) -> dict[str, Callable[..., str]]:
    """Bind tool handlers to the provided chat and calendar clients."""

    def handle_get_channels() -> str:
        channels = chat_client.get_channels()
        return json.dumps([_serialize_channel(c) for c in channels])

    def handle_get_channel(channel_id: str) -> str:
        channel = chat_client.get_channel(channel_id)
        return json.dumps(_serialize_channel(channel))

    def handle_get_messages(
        channel_id: str,
        limit: int = 10,
        cursor: str | None = None,
    ) -> str:
        messages = chat_client.get_messages(channel_id=channel_id, limit=limit, cursor=cursor)
        return json.dumps([_serialize_message(m) for m in messages])

    def handle_send_message(channel_id: str, text: str) -> str:
        message = chat_client.send_message(channel_id=channel_id, text=text)
        return json.dumps(_serialize_message(message))

    def handle_create_calendar_event(
        title: str,
        start_time: str,
        end_time: str,
        description: str | None = None,
        location: str | None = None,
    ) -> str:
        if calendar_client is None:
            return json.dumps({"error": "No calendar client configured."})
        start_dt = datetime.fromisoformat(start_time)
        end_dt = datetime.fromisoformat(end_time)
        created = cast("Any", calendar_client).create_event(
            title=title,
            start_time=start_dt,
            end_time=end_dt,
            description=description or "",
            location=location,
        )
        return _serialize_created_event(created)

    def handle_schedule_meeting_for_message(
        channel_id: str,
        message_id: str,
        start_time: str,
        end_time: str,
        location: str | None = None,
    ) -> str:
        if calendar_client is None:
            return json.dumps({"error": "No calendar client configured."})
        message = chat_client.get_message(message_id)
        start_dt = datetime.fromisoformat(start_time)
        end_dt = datetime.fromisoformat(end_time)
        title = f"Meeting: {message.text[:50]}"
        description = (
            f"Scheduled from Discord message by {message.sender} "
            f"in channel {channel_id}: {message.text}"
        )
        created = cast("Any", calendar_client).create_event(
            title=title,
            start_time=start_dt,
            end_time=end_dt,
            description=description,
            location=location,
        )
        return _serialize_created_event(created)

    return {
        "get_channels": handle_get_channels,
        "get_channel": handle_get_channel,
        "get_messages": handle_get_messages,
        "send_message": handle_send_message,
        "create_calendar_event": handle_create_calendar_event,
        "schedule_meeting_for_message": handle_schedule_meeting_for_message,
    }
