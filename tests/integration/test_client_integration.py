"""Integration tests for client dependency injection."""
from __future__ import annotations

import importlib
import json
from unittest.mock import MagicMock

import pytest

import chat_client_api

pytestmark = pytest.mark.integration


@pytest.fixture(autouse=True)
def reset_di_factory() -> None:
    """Reset DI so tests are isolated and order-independent."""
    chat_client_api.client._ClientRegistry._factory = None


@pytest.mark.circleci
def test_get_client_fails_without_implementation() -> None:
    """get_client() should raise before any implementation is imported."""
    with pytest.raises(RuntimeError, match="No chat client implementation registered"):
        chat_client_api.get_client()


@pytest.mark.circleci
def test_get_client_returns_discord_client_after_import(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Importing the implementation package should inject DiscordClient."""
    monkeypatch.setenv("DISCORD_BOT_TOKEN", "test-token")
    monkeypatch.setenv("DISCORD_GUILD_ID", "123456789")
    import discord_client_impl
    importlib.reload(discord_client_impl)
    client = chat_client_api.get_client()
    from discord_client_impl.client import DiscordClient
    assert isinstance(client, DiscordClient)


def test_get_ai_client_returns_openai_client_after_import(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Importing openai_ai_client_impl registers OpenAIAIClient."""
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("DISCORD_BOT_TOKEN", "test-token")
    monkeypatch.setenv("DISCORD_GUILD_ID", "123456789")

    import ai_client_api
    ai_client_api.client._factory = None  # reset AI registry
    chat_client_api.client._ClientRegistry._factory = None  # reset chat registry

    import discord_client_impl
    import openai_ai_client_impl
    importlib.reload(discord_client_impl)
    importlib.reload(openai_ai_client_impl)

    from ai_client_api import get_client
    from openai_ai_client_impl.client import OpenAIAIClient

    client = get_client()
    assert isinstance(client, OpenAIAIClient)


def test_ai_tool_call_creates_calendar_event(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Integration: AI tool-call → calendar action via mocked OpenAI + calendar client.

    Verifies the full AI → tool dispatch → cross-vertical calendar path.
    """
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("DISCORD_BOT_TOKEN", "test-token")
    monkeypatch.setenv("DISCORD_GUILD_ID", "123456789")

    from chat_client_api import Channel, Message
    from datetime import UTC, datetime
    from openai_ai_client_impl.client import OpenAIAIClient

    # --- Fake chat client ---
    from chat_client_api import ChatClient

    class FakeChatClient(ChatClient):
        def get_channels(self) -> list[Channel]:
            return [Channel(channel_id="123", name="general", is_private=False, channel_type="group")]

        def get_channel(self, channel_id: str) -> Channel:
            return Channel(channel_id=channel_id, name="general", is_private=False, channel_type="group")

        def get_messages(self, channel_id: str, limit: int = 10, cursor: str | None = None) -> list[Message]:
            return []

        def get_message(self, message_id: str) -> Message:
            return Message(
                message_id=message_id,
                channel="123",
                text="discuss the project",
                sender="alice",
                timestamp=datetime.now(UTC),
            )

        def send_message(self, channel_id: str, text: str) -> Message:
            return Message(message_id="m1", channel=channel_id, text=text, sender="bot", timestamp=datetime.now(UTC))

        def delete_message(self, message_id: str) -> None:
            return None

    # --- Fake calendar client ---
    mock_calendar = MagicMock()
    created_event = MagicMock()
    created_event.id = "evt-1"
    created_event.title = "Meeting: discuss the project"
    created_event.start_time = datetime(2026, 5, 10, 15, 0, tzinfo=UTC)
    created_event.end_time = datetime(2026, 5, 10, 16, 0, tzinfo=UTC)
    created_event.description = "Scheduled from Discord"
    created_event.location = None
    mock_calendar.create_event.return_value = created_event

    # --- Mock OpenAI to return a schedule_meeting_for_message tool call ---
    tool_call = MagicMock()
    tool_call.id = "call-1"
    tool_call.type = "function"
    tool_call.function.name = "schedule_meeting_for_message"
    tool_call.function.arguments = json.dumps({
        "channel_id": "123",
        "message_id": "m1",
        "start_time": "2026-05-10T15:00:00+00:00",
        "end_time": "2026-05-10T16:00:00+00:00",
    })

    # First response: tool call
    first_message = MagicMock()
    first_message.content = None
    first_message.tool_calls = [tool_call]

    # Second response: final answer
    second_message = MagicMock()
    second_message.content = "Meeting scheduled successfully!"
    second_message.tool_calls = None

    mock_openai = MagicMock()
    mock_openai.chat.completions.create.side_effect = [
        MagicMock(choices=[MagicMock(message=first_message)]),
        MagicMock(choices=[MagicMock(message=second_message)]),
    ]

    # --- Wire everything together ---
    ai_client = OpenAIAIClient(
        chat_client=FakeChatClient(),
        calendar_client=mock_calendar,
    )
    ai_client._client = mock_openai

    result = ai_client.run("Schedule a meeting for message m1 from channel 123")

    assert result == "Meeting scheduled successfully!"
    mock_calendar.create_event.assert_called_once()

def test_ai_tool_call_real_openai_and_calendar(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Real integration test: OpenAI API → schedule_meeting_for_message → Google Calendar.

    Requires OPENAI_API_KEY env var and valid credentials.json + token.json.
    Skipped automatically if any credential is missing.
    """
    import os
    from pathlib import Path

    if not os.environ.get("OPENAI_API_KEY"):
        pytest.skip("OPENAI_API_KEY not set")
    if not Path("credentials.json").exists():
        pytest.skip("credentials.json not found")
    if not Path("token.json").exists():
        pytest.skip("token.json not found")

    from datetime import UTC, datetime
    from chat_client_api import Channel, ChatClient, Message
    from openai_ai_client_impl.client import OpenAIAIClient
    from google_calendar_adapter.client import get_connected_calendar_client

    # Real calendar client
    calendar_client = get_connected_calendar_client()

    # Fake chat client with a real-looking message
    class FakeChatClient(ChatClient):
        def get_channels(self) -> list[Channel]:
            return [Channel(channel_id="123", name="general", is_private=False, channel_type="group")]

        def get_channel(self, channel_id: str) -> Channel:
            return Channel(channel_id=channel_id, name="general", is_private=False, channel_type="group")

        def get_messages(
            self, channel_id: str, limit: int = 10, cursor: str | None = None
        ) -> list[Message]:
            return []

        def get_message(self, message_id: str) -> Message:
            return Message(
                message_id=message_id,
                channel="123",
                text="Team sync to discuss HW3 final submission",
                sender="alice",
                timestamp=datetime.now(UTC),
            )

        def send_message(self, channel_id: str, text: str) -> Message:
            return Message(
                message_id="m1",
                channel=channel_id,
                text=text,
                sender="bot",
                timestamp=datetime.now(UTC),
            )

        def delete_message(self, message_id: str) -> None:
            return None

    ai_client = OpenAIAIClient(
        chat_client=FakeChatClient(),
        calendar_client=calendar_client,
    )

    response = ai_client.run(
        "Schedule a meeting for message m1 from channel 123 "
        "for tomorrow at 3pm to 4pm UTC"
    )

    assert isinstance(response, str)
    assert len(response) > 0
