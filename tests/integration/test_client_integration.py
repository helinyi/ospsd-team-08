"""Integration tests for client dependency injection."""
import pytest
import discord_client_impl # Import to trigger dependency injection
from chat_client_api import get_client, ChatClient
pytestmark = pytest.mark.integration

@pytest.mark.circleci
def test_dependency_injection_works() -> None:
    """
    Verify that importing the implementation package injects DiscordClient.
    """
    client = get_client()

    from discord_client_api.client import DiscordClient

    assert isinstance(client, DiscordClient), (
        "Dependency Injection failed: get_client() did not return DiscordClient"
    )
    # Also check that client has required methods
    assert hasattr(client, "get_channels")
    assert hasattr(client, "get_messages")
    assert hasattr(client, "send_message")

def test_multiple_get_client_instances_are_separate() -> None:
    """Ensure each call to get_client() returns a new instance."""
    client1 = get_client()
    client2 = get_client()
    assert client1 is not client2, "get_client() should return separate instances"
