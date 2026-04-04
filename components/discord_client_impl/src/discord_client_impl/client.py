"""Concrete Discord implementation of the ChatClient interface."""

from __future__ import annotations

import os
from datetime import UTC, datetime

import requests
from chat_client_api.client import ChatClient
from chat_client_api.models import Channel, Message

from discord_client_impl.auth import DiscordAuthenticator, DiscordOAuthHandler


class DiscordClient(ChatClient):
    """Discord implementation of the ChatClient abstract interface."""

    _DISCORD_API_BASE = "https://discord.com/api/v10"

    def __init__(
        self,
        authenticator: DiscordAuthenticator | None = None,
        access_token: str | None = None,
    ) -> None:
        """Initialize the Discord client.

        Args:
            authenticator: Optional authenticator. If not provided, loads from env.
            access_token: Optional access token. If provided, used for authentication.

        """
        if access_token:
            self._headers = DiscordOAuthHandler.get_oauth_headers(access_token)
        else:
            self._auth = authenticator or DiscordAuthenticator.from_env()
            self._headers = self._auth.get_headers()

        guild_id = os.getenv("DISCORD_GUILD_ID")
        if not guild_id:
            msg = "Missing required environment variable: DISCORD_GUILD_ID"
            raise RuntimeError(msg)
        self._guild_id = guild_id

    def get_channels(self) -> list[Channel]:
        """Retrieve all text channels from the Discord guild.

        Returns:
            A list of text channels in the guild.

        Raises:
            RuntimeError: If the API call fails.

        """
        url = f"{self._DISCORD_API_BASE}/guilds/{self._guild_id}/channels"
        try:
            response = requests.get(url, headers=self._headers, timeout=10)
        except requests.RequestException as exc:
            msg = f"Failed to fetch channels: {exc}"
            raise RuntimeError(msg) from exc

        if not response.ok:
            msg = f"Discord API returned status {response.status_code} fetching channels"
            raise RuntimeError(msg)

        raw_channels: list[dict[str, object]] = response.json()
        return [
            Channel(
                id=str(channel["id"]),
                name=str(channel["name"]),
            )
            for channel in raw_channels
            if channel.get("type") == 0  # 0 = text channel
        ]

    def get_messages(self, channel: Channel, limit: int = 10) -> list[Message]:
        """Retrieve recent messages from a Discord channel.

        Args:
            channel: The channel to fetch messages from.
            limit: Maximum number of messages to retrieve.

        Returns:
            A list of recent messages ordered oldest to newest.

        Raises:
            RuntimeError: If the API call fails.

        """
        url = f"{self._DISCORD_API_BASE}/channels/{channel.id}/messages"
        params = {"limit": limit}
        try:
            response = requests.get(
                url,
                headers=self._headers,
                params=params,
                timeout=10,
            )
        except requests.RequestException as exc:
            msg = f"Failed to fetch messages: {exc}"
            raise RuntimeError(msg) from exc

        if not response.ok:
            msg = f"Discord API returned status {response.status_code} fetching messages"
            raise RuntimeError(msg)

        raw_messages: list[dict[str, object]] = response.json()
        messages = [
            Message(
                id=str(raw["id"]),
                channel=channel,
                sender=str(
                    raw["author"]["username"]  # type: ignore[index]
                    if isinstance(raw.get("author"), dict)
                    else "unknown"
                ),
                content=str(raw.get("content", "")),
                timestamp=datetime.fromisoformat(
                    str(raw["timestamp"])
                ).replace(tzinfo=UTC),
            )
            for raw in raw_messages
        ]
        return list(reversed(messages))

    def send_message(self, channel: Channel, content: str) -> Message:
        """Send a message to a Discord channel.

        Args:
            channel: The channel to send to.
            content: The message content.

        Returns:
            The sent message.

        Raises:
            RuntimeError: If the API call fails.

        """
        url = f"{self._DISCORD_API_BASE}/channels/{channel.id}/messages"
        payload = {"content": content}
        try:
            response = requests.post(
                url,
                headers=self._headers,
                json=payload,
                timeout=10,
            )
        except requests.RequestException as exc:
            msg = f"Failed to send message: {exc}"
            raise RuntimeError(msg) from exc

        if not response.ok:
            msg = f"Discord API returned status {response.status_code} sending message"
            raise RuntimeError(msg)

        raw: dict[str, object] = response.json()
        return Message(
            id=str(raw["id"]),
            channel=channel,
            sender=str(
                raw["author"]["username"]  # type: ignore[index]
                if isinstance(raw.get("author"), dict)
                else "unknown"
            ),
            content=str(raw.get("content", "")),
            timestamp=datetime.fromisoformat(
                str(raw["timestamp"])
            ).replace(tzinfo=UTC),
        )
