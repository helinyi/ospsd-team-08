"""Discord Bot Token authentication."""

from __future__ import annotations

import os

import requests

_HTTP_UNAUTHORIZED = 401


class DiscordAuthenticator:
    """Encapsulates Discord Bot Token authentication."""

    _DISCORD_API_BASE = "https://discord.com/api/v10"

    def __init__(self, token: str) -> None:
        """Initialize with a Bot Token string."""
        self._token = token

    @classmethod
    def from_env(cls) -> DiscordAuthenticator:
        """Create an authenticator from the DISCORD_BOT_TOKEN environment variable."""
        token = os.getenv("DISCORD_BOT_TOKEN")
        if not token:
            msg = "Missing required environment variable: DISCORD_BOT_TOKEN"
            raise RuntimeError(msg)
        return cls(token)

    def get_headers(self) -> dict[str, str]:
        """Return HTTP headers required for Discord API requests."""
        return {
            "Authorization": f"Bot {self._token}",
            "Content-Type": "application/json",
        }

    def validate(self) -> None:
        """Verify the token is valid by calling GET /users/@me.

        Raises:
            RuntimeError: If the token is invalid (401) or an unexpected error occurs.

        """
        url = f"{self._DISCORD_API_BASE}/users/@me"
        try:
            response = requests.get(url, headers=self.get_headers(), timeout=10)
        except requests.RequestException as exc:
            msg = f"Discord API request failed: {exc}"
            raise RuntimeError(msg) from exc

        if response.status_code == _HTTP_UNAUTHORIZED:
            msg = "Discord token is invalid or unauthorized (401)"
            raise RuntimeError(msg)
        if not response.ok:
            msg = f"Discord API returned unexpected status {response.status_code}"
            raise RuntimeError(msg)
