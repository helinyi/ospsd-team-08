from __future__ import annotations

import json

from datetime import UTC, datetime
from chat_client_api import ChatClient
from chat_client_api import Channel, Message
from openai_ai_client_impl.tools import get_tool_handlers


class FakeChatClient(ChatClient):
    def get_channels(self) -> list[Channel]:
        return [
            Channel(channel_id="123", name="general", is_private=False, channel_type="group")
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
