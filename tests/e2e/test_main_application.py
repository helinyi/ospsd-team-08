"""ospsd-team-08/tests/e2e/test_main_application.py"""

from __future__ import annotations

import pytest

import chat_client_api


@pytest.mark.e2e
def test_e2e_workflow_send_and_fetch_message() -> None:
    # Import implementation to register Dependency Injection
    import discord_client_impl  # noqa: F401

    client = chat_client_api.get_client()

    # 1) Channels exist
    channels = client.get_channels()
    assert isinstance(channels, list)
    assert len(channels) >= 1

    channel_id = channels[0].id

    # 2) Send message
    sent = client.send_message(channel_id, "e2e: hello")

    # 3) Fetch messages and confirm round-trip
    msgs = client.get_messages(channel_id, limit=10)
    assert any(m.id == sent.id and m.content == "e2e: hello" for m in msgs)
