"""Discord authentication: Bot Token and OAuth 2.0."""

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


class DiscordOAuthHandler:
    """Handles Discord OAuth 2.0 Authorization Code Flow."""

    _DISCORD_API_BASE = "https://discord.com/api/v10"
    _AUTHORIZATION_URL = "https://discord.com/oauth2/authorize"
    _TOKEN_URL = "https://discord.com/api/oauth2/token" # noqa: S105 - This is a URL, not a password

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        redirect_uri: str,
    ) -> None:
        """Initialize with OAuth 2.0 credentials."""
        self._client_id = client_id
        self._client_secret = client_secret
        self._redirect_uri = redirect_uri

    @classmethod
    def from_env(cls) -> DiscordOAuthHandler:
        """Create an OAuth handler from environment variables.

        Raises:
            RuntimeError: If any required environment variable is missing.

        """
        client_id = os.getenv("DISCORD_CLIENT_ID")
        client_secret = os.getenv("DISCORD_CLIENT_SECRET")
        redirect_uri = os.getenv(
            "DISCORD_REDIRECT_URI",
            "http://localhost:8000/auth/callback",
        )

        if not client_id:
            msg = "Missing required environment variable: DISCORD_CLIENT_ID"
            raise RuntimeError(msg)
        if not client_secret:
            msg = "Missing required environment variable: DISCORD_CLIENT_SECRET"
            raise RuntimeError(msg)

        return cls(client_id, client_secret, redirect_uri)

    def get_authorization_url(self) -> str:
        """Generate the Discord OAuth2 authorization URL.

        Returns:
            The URL to redirect the user to for Discord login.

        """
        params = {
            "client_id": self._client_id,
            "redirect_uri": self._redirect_uri,
            "response_type": "code",
            "scope": "identify guilds",
        }
        param_string = "&".join(f"{k}={v}" for k, v in params.items())
        return f"{self._AUTHORIZATION_URL}?{param_string}"

    def exchange_code(self, code: str) -> str:
        """Exchange an authorization code for an access token.

        Args:
            code: The authorization code received from Discord callback.

        Returns:
            The access token string.

        Raises:
            RuntimeError: If the token exchange fails.

        """
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self._redirect_uri,
        }
        try:
            response = requests.post(
                self._TOKEN_URL,
                data=data,
                auth=(self._client_id, self._client_secret),
                timeout=10,
            )
        except requests.RequestException as exc:
            msg = f"Token exchange request failed: {exc}"
            raise RuntimeError(msg) from exc

        if not response.ok:
            msg = f"Token exchange failed with status {response.status_code}"
            raise RuntimeError(msg)

        token_data: dict[str, str] = response.json()
        return token_data["access_token"]

    @staticmethod
    def get_oauth_headers(access_token: str) -> dict[str, str]:
        """Return HTTP headers for OAuth user token requests.

        Args:
            access_token: The OAuth access token for the user.

        """
        return {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }
