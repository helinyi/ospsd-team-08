"""Tool definitions and handlers for the OpenAI AI client."""

from __future__ import annotations

import json
from datetime import datetime
from typing import TYPE_CHECKING, Any, cast

from google_calendar_adapter.client import get_connected_calendar_client

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import Callable

    from chat_client_api import Channel, ChatClient, Message


def build_openai_tools() -> list[dict[str, Any]]:
    """Return OpenAI tool definitions for the shared chat API."""
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
                "parameters": {
                    "type": "object",
                    "properties": {
                        "channel_id": {
                            "type": "string",
                            "description": "The target channel ID.",
                        }
                    },
                    "required": ["channel_id"],
                    "additionalProperties": False,
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_messages",
                "description": "Get recent messages from a channel.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "channel_id": {
                            "type": "string",
                            "description": "The target channel ID.",
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of messages to return.",
                            "default": 10,
                        },
                        "cursor": {
                            "type": ["string", "null"],
                            "description": "Optional pagination cursor.",
                        },
                    },
                    "required": ["channel_id"],
                    "additionalProperties": False,
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "send_message",
                "description": "Send a message to a channel.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "channel_id": {
                            "type": "string",
                            "description": "The target channel ID.",
                        },
                        "text": {
                            "type": "string",
                            "description": "The message content to send.",
                        },
                    },
                    "required": ["channel_id", "text"],
                    "additionalProperties": False,
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "create_calendar_event",
                "description": "Create a Google Calendar event. Use this for cross-vertical calendar scheduling actions.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "The event title.",
                        },
                        "start_time": {
                            "type": "string",
                            "description": "Event start time as an ISO datetime string, e.g. 2026-05-10T15:00:00+00:00.",
                        },
                        "end_time": {
                            "type": "string",
                            "description": "Event end time as an ISO datetime string, e.g. 2026-05-10T16:00:00+00:00.",
                        },
                        "description": {
                            "type": ["string", "null"],
                            "description": "Optional event description.",
                        },
                        "location": {
                            "type": ["string", "null"],
                            "description": "Optional event location.",
                        },
                    },
                    "required": ["title", "start_time", "end_time"],
                    "additionalProperties": False,
                },
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


def _get_calendar_client(calendar_client: object | None) -> object:
    """Return the provided calendar client or create a connected one."""
    if calendar_client is not None:
        return calendar_client

    return get_connected_calendar_client()


def _create_calendar_event(  # noqa: PLR0913
    calendar_client: object | None,
    title: str,
    start_time: str,
    end_time: str,
    description: str | None = None,
    location: str | None = None,
) -> str:
    """Create a Google Calendar event and return a serialized result."""
    client = cast("Any", _get_calendar_client(calendar_client))

    start_dt = datetime.fromisoformat(start_time)
    end_dt = datetime.fromisoformat(end_time)

    body: dict[str, object] = {
        "summary": title,
        "start": {
            "dateTime": start_dt.isoformat(),
            "timeZone": "UTC",
        },
        "end": {
            "dateTime": end_dt.isoformat(),
            "timeZone": "UTC",
        },
    }

    if description:
        body["description"] = description

    if location:
        body["location"] = location

    service = client._require_calendar_service()  # noqa: SLF001
    calendar_id = getattr(client, "calendar_id", "primary")

    response = service.events().insert(
        calendarId=calendar_id,
        body=body,
    ).execute()

    return json.dumps(
        {
            "event_id": response.get("id"),
            "title": response.get("summary"),
            "start_time": response.get("start", {}).get("dateTime"),
            "end_time": response.get("end", {}).get("dateTime"),
            "location": response.get("location"),
            "description": response.get("description"),
        }
    )


def get_tool_handlers(
    chat_client: ChatClient,
    calendar_client: object | None = None,
) -> dict[str, Callable[..., str]]:
    """Bind tool handlers to the provided chat and calendar clients."""

    def handle_get_channels() -> str:
        channels = chat_client.get_channels()
        return json.dumps([_serialize_channel(channel) for channel in channels])

    def handle_get_channel(channel_id: str) -> str:
        channel = chat_client.get_channel(channel_id)
        return json.dumps(_serialize_channel(channel))

    def handle_get_messages(
        channel_id: str,
        limit: int = 10,
        cursor: str | None = None,
    ) -> str:
        messages = chat_client.get_messages(
            channel_id=channel_id,
            limit=limit,
            cursor=cursor,
        )
        return json.dumps([_serialize_message(message) for message in messages])

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
        return _create_calendar_event(
            calendar_client=calendar_client,
            title=title,
            start_time=start_time,
            end_time=end_time,
            description=description,
            location=location,
        )

    return {
        "get_channels": handle_get_channels,
        "get_channel": handle_get_channel,
        "get_messages": handle_get_messages,
        "send_message": handle_send_message,
        "create_calendar_event": handle_create_calendar_event,
    }
