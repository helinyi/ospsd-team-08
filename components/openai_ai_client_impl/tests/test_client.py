from __future__ import annotations

import json
from typing import Any

from chat_client_api import Channel, Message
from openai_ai_client_impl.client import OpenAIAIClient


class FakeChatClient:
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
                timestamp="2026-04-17T21:00:00Z",
            )
        ]

    def get_message(self, message_id: str) -> Message:
        return Message(
            message_id=message_id,
            channel="123",
            text="hello",
            sender="bot",
            timestamp="2026-04-17T21:00:00Z",
        )

    def delete_message(self, message_id: str) -> None:
        return None

    def send_message(self, channel_id: str, text: str) -> Message:
        return Message(
            message_id="m2",
            channel=channel_id,
            text=text,
            sender="me",
            timestamp="2026-04-17T21:01:00Z",
        )


class FakeToolCall:
    def __init__(self, name: str, arguments: dict[str, Any]) -> None:
        self.id = "call_1"
        self.type = "function"
        self.function = type(
            "Func",
            (),
            {
                "name": name,
                "arguments": json.dumps(arguments),
            },
        )()


class FakeMessage:
    def __init__(
        self,
        content: str | None = None,
        tool_calls: list[Any] | None = None,
    ) -> None:
        self.content = content
        self.tool_calls = tool_calls


class FakeResponse:
    def __init__(self, message: FakeMessage) -> None:
        self.choices = [type("Choice", (), {"message": message})()]


class FakeCompletions:
    def __init__(self) -> None:
        self._step = 0

    def create(self, *args: Any, **kwargs: Any) -> FakeResponse:
        if self._step == 0:
            self._step += 1
            return FakeResponse(
                FakeMessage(
                    tool_calls=[FakeToolCall("get_channels", {})]
                )
            )

        return FakeResponse(
            FakeMessage(content="Channels retrieved successfully.")
        )


class FakeChat:
    def __init__(self) -> None:
        self.completions = FakeCompletions()


class FakeOpenAIClient:
    def __init__(self) -> None:
        self.chat = FakeChat()


def test_run_with_tool_call() -> None:
    ai_client = OpenAIAIClient(chat_client=FakeChatClient())
    ai_client._client = FakeOpenAIClient()

    result = ai_client.run("show channels")

    assert "Channels retrieved" in result