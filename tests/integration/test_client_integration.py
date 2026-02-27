"""Integration tests for client dependency injection."""
import pytest

pytestmark = pytest.mark.integration


@pytest.mark.circleci
def test_get_client_fails_without_implementation() -> None:
    """Verify that get_client() fails before any implementation is registered."""
    from chat_client_api import get_client

    with pytest.raises(RuntimeError, match="No ChatClient implementation registered"):
        get_client()


@pytest.mark.circleci
def test_dependency_injection_works() -> None:
    """Verify that importing the implementation package injects DiscordClient."""
    import discord_client_impl  # noqa: F401 - Triggers DI registration
    from chat_client_api import get_client
    from discord_client_impl.client import DiscordClient

    client = get_client()

    assert isinstance(client, DiscordClient), (
        "Dependency Injection failed: get_client() did not return DiscordClient"
    )
    # Also check that client has required methods
    assert hasattr(client, "get_channels")
    assert hasattr(client, "get_messages")
    assert hasattr(client, "send_message")


def test_multiple_get_client_instances_are_separate() -> None:
    """Ensure each call to get_client() returns a new instance."""
    from chat_client_api import get_client

    client1 = get_client()
    client2 = get_client()
    assert client1 is not client2, "get_client() should return separate instances"


def test_get_messages_valid_channel() -> None:
    """Verify get_messages works with a valid channel."""
    from chat_client_api import get_client

    client = get_client()
    messages = client.get_messages("general")
    assert isinstance(messages, list)


def test_get_messages_invalid_channel() -> None:
    """Verify get_messages raises ValueError for non-existent channel."""
    from chat_client_api import get_client

    client = get_client()
    with pytest.raises(ValueError, match="does not exist"):
        client.get_messages("nonexistent")


def test_send_message_valid_channel() -> None:
    """Verify send_message works with a valid channel."""
    from chat_client_api import get_client

    client = get_client()
    msg = client.send_message("general", "Hello world")
    assert msg.content == "Hello world"
    assert msg.channel_id == "general"


def test_send_message_invalid_channel() -> None:
    """Verify send_message raises ValueError for non-existent channel."""
    from chat_client_api import get_client

    client = get_client()
    with pytest.raises(ValueError, match="does not exist"):
        client.send_message("nonexistent", "test message")
