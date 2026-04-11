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

