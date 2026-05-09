"""Tests for ai_client_api DI registry."""
from __future__ import annotations

from typing import Any

import pytest

import ai_client_api
from ai_client_api import AIClient, get_client, register_client


class FakeAIClient(AIClient):
    """Minimal AIClient implementation for testing."""

    def run(self, user_input: str, context: dict[str, Any] | None = None) -> str:
        return f"response to: {user_input}"


@pytest.fixture(autouse=True)
def reset_factory() -> None:
    """Reset the AI client factory between tests."""
    ai_client_api.client._factory = None


def test_get_client_raises_without_registration() -> None:
    """get_client() should raise before any implementation is registered."""
    with pytest.raises(RuntimeError, match="No AI client implementation registered"):
        get_client()


def test_get_client_returns_registered_client() -> None:
    """get_client() should return the registered implementation."""
    register_client(FakeAIClient)
    client = get_client()
    assert isinstance(client, FakeAIClient)


def test_registered_client_runs() -> None:
    """Registered client should be callable via get_client()."""
    register_client(FakeAIClient)
    client = get_client()
    result = client.run("hello")
    assert result == "response to: hello"
