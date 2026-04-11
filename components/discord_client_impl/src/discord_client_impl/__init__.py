"""Discord Client Implementation — registers via Dependency Injection.

Importing this package registers the DiscordClient as the
concrete implementation for chat_client_api.get_client().
"""

from chat_client_api import register_client

from discord_client_impl.client import DiscordClient


def _create_discord_client() -> DiscordClient: # pragma: no cover, requires actual Discord credentials
    """Create a DiscordClient instance."""
    return DiscordClient()


register_client(_create_discord_client)
