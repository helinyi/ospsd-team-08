# components/chat_client_api/tests/test_di_registration.py

from __future__ import annotations

from datetime import UTC, datetime

import pytest

import chat_client_api
from chat_client_api.client import ChatClient
from chat_client_api.models import Message


@pytest.fixture(autouse=True)
def reset_di_factory() -> None:
    # Reset global state so tests are order-independent and isolated
    chat_client_api._client_factory = chat_client_api._default_factory


class FakeClient(ChatClient):
    def get_channels(self):
        return []

    def get_messages(self, channel_id: str, limit: int = 10):
        return []

    def send_message(self, channel_id: str, content: str) -> Message:
        return Message(
            id="test",
            channel_id=channel_id,
            sender="me",
            content=content,
            timestamp=datetime.now(UTC),
        )


def test_get_client_raises_when_unregistered() -> None:
    with pytest.raises(RuntimeError, match="No ChatClient implementation registered"):
        chat_client_api.get_client()


def test_register_client_factory_returns_client() -> None:
    chat_client_api.register_client_factory(lambda: FakeClient())

    client = chat_client_api.get_client()
    assert isinstance(client, FakeClient)
