"""End-to-end tests for the chat client workflow (DI + implementation + interface).

Requires real Discord credentials set as environment variables:
    - DISCORD_BOT_TOKEN
    - DISCORD_GUILD_ID

These tests run against the real Discord API and are skipped if credentials are missing.
"""
# tests/e2e/test_main_application.py

from __future__ import annotations

import os
import time

import pytest

import chat_client_api


def credentials_available() -> bool:
    """Check if real Discord credentials are available."""
    return bool(os.getenv("DISCORD_BOT_TOKEN") and os.getenv("DISCORD_GUILD_ID"))


@pytest.mark.e2e
@pytest.mark.skipif(
    not credentials_available(),
    reason="Discord credentials not available in environment",
)
def test_e2e_workflow_send_and_fetch_message() -> None:
    """Full round-trip: get channels, send message, fetch and verify."""
    import discord_client_impl  # noqa: F401

    client = chat_client_api.get_client()

    # 1) Channels exist
    channels = client.get_channels()
    assert isinstance(channels, list)
    assert len(channels) >= 1

    channel = channels[0]

    # 2) Send message using new signature
    sent = client.send_message(channel.channel_id, "e2e: hello")
    assert sent.text == "e2e: hello"

    # 3) Wait briefly for Discord to process
    time.sleep(1)

    # 4) Fetch messages and confirm round-trip
    msgs = client.get_messages(channel.channel_id, limit=10)
    assert any(m.message_id == sent.message_id and m.text == "e2e: hello" for m in msgs)
