"""Integration tests for client dependency injection."""

from __future__ import annotations

import importlib

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

    import importlib
    import ai_client_api
    import chat_client_api
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

