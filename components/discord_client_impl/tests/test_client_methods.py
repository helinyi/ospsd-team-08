"""Unit tests for discord_client_impl."""
# components/discord_client_impl/tests/test_client_methods.py

from __future__ import annotations

from datetime import UTC

import pytest

from chat_client_api.models import Channel, Message
from discord_client_impl.client import DiscordClient


def test_get_channels_returns_copy_and_has_general_channel() -> None:
    client = DiscordClient()

    channels = client.get_channels()
    assert isinstance(channels, list)
    assert all(isinstance(c, Channel) for c in channels)

    assert any(c.id == "general" for c in channels)

    channels.append(Channel(id="fake", name="fake"))
    channels2 = client.get_channels()
    assert not any(c.id == "fake" for c in channels2)


def test_send_message_to_existing_channel_stores_and_returns_message() -> None:
    client = DiscordClient()

    channels = client.get_channels()
    assert isinstance(channels, list)
    assert all(isinstance(c, Channel) for c in channels)

    assert any(c.id == "general" for c in channels)

    general = channels[0]

    msg = client.send_message(general, "hello")

    assert isinstance(msg, Message)
    assert msg.channel == general
    assert msg.content == "hello"
    assert msg.sender == "me"

    assert msg.timestamp.tzinfo is not None
    assert msg.timestamp.tzinfo == UTC

    messages = client.get_messages(general)
    assert len(messages) == 1
    assert messages[0].id == msg.id
    assert messages[0].content == "hello"


def test_get_messages_returns_last_n_in_order() -> None:
    client = DiscordClient()

    channels = client.get_channels()
    assert isinstance(channels, list)
    assert all(isinstance(c, Channel) for c in channels)

    assert any(c.id == "general" for c in channels)

    general = channels[0]

    # Send 5 messages
    for i in range(5):
        client.send_message(general, f"msg{i}")

    # Ask for last 3
    msgs = client.get_messages(general, limit=3)
    assert [m.content for m in msgs] == ["msg2", "msg3", "msg4"]


def test_get_messages_limit_larger_than_total_returns_all() -> None:
    client = DiscordClient()

    channels = client.get_channels()
    assert isinstance(channels, list)
    assert all(isinstance(c, Channel) for c in channels)

    assert any(c.id == "general" for c in channels)

    general = channels[0]

    client.send_message(general, "a")
    client.send_message(general, "b")

    msgs = client.get_messages(general, limit=10)
    assert [m.content for m in msgs] == ["a", "b"]


def test_get_messages_default_limit_is_10() -> None:
    client = DiscordClient()

    channels = client.get_channels()
    assert isinstance(channels, list)
    assert all(isinstance(c, Channel) for c in channels)

    assert any(c.id == "general" for c in channels)

    general = channels[0]

    for i in range(15):
        client.send_message(general, f"m{i}")

    msgs = client.get_messages(general)  # default limit=10
    assert len(msgs) == 10
    assert [m.content for m in msgs] == [f"m{i}" for i in range(5, 15)]


def test_send_message_raises_for_nonexistent_channel() -> None:
    client = DiscordClient()

    nope = Channel(id="nope", name="nope")
    with pytest.raises(ValueError, match=r"Channel with id 'nope' does not exist"):
        client.send_message(nope, "hi")


def test_get_messages_raises_for_nonexistent_channel() -> None:
    client = DiscordClient()

    nope = Channel(id="nope", name="nope")
    with pytest.raises(ValueError, match=r"Channel with id 'nope' does not exist"):
        client.get_messages(nope, limit=1)
