"""Tool definitions and handlers for the OpenAI AI client."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

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


def get_tool_handlers(chat_client: ChatClient) -> dict[str, Callable[..., str]]:
    """Bind tool handlers to the provided chat client."""

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

    return {
        "get_channels": handle_get_channels,
        "get_channel": handle_get_channel,
        "get_messages": handle_get_messages,
        "send_message": handle_send_message,
    }
