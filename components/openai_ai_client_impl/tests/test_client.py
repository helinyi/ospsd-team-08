from __future__ import annotations

import json
from typing import Any, cast
from datetime import UTC, datetime
from chat_client_api import ChatClient
from chat_client_api import Channel, Message
from openai_ai_client_impl.client import OpenAIAIClient

import pytest


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


def test_run_with_tool_call(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "test-openai-key")

    ai_client = OpenAIAIClient(chat_client=FakeChatClient())
    ai_client._client = cast("Any", FakeOpenAIClient())

    result = ai_client.run("show channels")

    assert "Channels retrieved" in result

def test_raises_without_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(ValueError, match="OPENAI_API_KEY"):
        OpenAIAIClient(chat_client=FakeChatClient())


def test_run_returns_direct_response(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test when model responds without tool calls."""
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")

    class DirectResponseCompletions:
        def create(self, *args: Any, **kwargs: Any) -> FakeResponse:
            return FakeResponse(FakeMessage(content="Hello there!"))

    class DirectChat:
        completions = DirectResponseCompletions()

    ai_client = OpenAIAIClient(chat_client=FakeChatClient())
    ai_client._client = cast("Any", type("C", (), {"chat": DirectChat()})())

    result = ai_client.run("hello")
    assert result == "Hello there!"


def test_run_with_context(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test run with extra context."""
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")

    class DirectResponseCompletions:
        def create(self, *args: Any, **kwargs: Any) -> FakeResponse:
            return FakeResponse(FakeMessage(content="Done."))

    class DirectChat:
        completions = DirectResponseCompletions()

    ai_client = OpenAIAIClient(chat_client=FakeChatClient())
    ai_client._client = cast("Any", type("C", (), {"chat": DirectChat()})())

    result = ai_client.run("hello", context={"key": "value"})
    assert result == "Done."

def test_run_with_extra_tool_handlers(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that extra_tool_handlers are merged into tool handlers."""
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    extra = {"custom_tool": lambda: json.dumps({"result": "custom"})}
    ai_client = OpenAIAIClient(chat_client=FakeChatClient(), extra_tool_handlers=extra)
    assert "custom_tool" in ai_client._tool_handlers

def test_run_raises_tool_loop_exhausted(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that ToolLoopExhaustedError is raised after max iterations."""
    import pytest
    from ai_client_api import ToolLoopExhaustedError

    monkeypatch.setenv("OPENAI_API_KEY", "test-key")

    class InfiniteToolCompletions:
        def create(self, *args: Any, **kwargs: Any) -> FakeResponse:
            return FakeResponse(FakeMessage(tool_calls=[FakeToolCall("get_channels", {})]))

    class InfiniteChat:
        completions = InfiniteToolCompletions()

    ai_client = OpenAIAIClient(chat_client=FakeChatClient())
    ai_client._client = cast("Any", type("C", (), {"chat": InfiniteChat()})())

    with pytest.raises(ToolLoopExhaustedError):
        ai_client.run("keep calling tools")
