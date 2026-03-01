"""End-to-end tests for the main application."""
import os
import pytest
from chat_client_api import get_client


@pytest.mark.e2e
def test_e2e_authentication():
    token = os.getenv("DISCORD_BOT_TOKEN")
    if not token:
        pytest.skip("DISCORD_BOT_TOKEN not set")

    import discord_client_impl  # register DI

    client = get_client()

    # call a real API method
    channels = client.get_channels()
    assert isinstance(channels, list)
