"""Concrete Discord implementation of the ChatClient interface."""

from __future__ import annotations

import os
from datetime import UTC, datetime

import requests
from chat_client_api import Channel, ChatClient, Message

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
        """Retrieve all text channels from the Discord guild."""
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
                channel_id=str(channel["id"]),
                name=str(channel["name"]),
            )
            for channel in raw_channels
            if channel.get("type") == 0
        ]

    def get_channel(self, channel_id: str) -> Channel:
        """Get a single channel by ID.

        Args:
            channel_id: The channel ID to retrieve.

        Returns:
            Channel object.

        Raises:
            ValueError: If the channel is not found.

        """
        url = f"{self._DISCORD_API_BASE}/channels/{channel_id}"
        try:
            response = requests.get(url, headers=self._headers, timeout=10)
        except requests.RequestException as exc:
            msg = f"Failed to fetch channel: {exc}"
            raise RuntimeError(msg) from exc

        if response.status_code == 404:  # noqa: PLR2004
            msg = f"Channel with id '{channel_id}' does not exist."
            raise ValueError(msg)

        if not response.ok:
            msg = f"Discord API returned status {response.status_code} fetching channel"
            raise RuntimeError(msg)

        raw: dict[str, object] = response.json()
        return Channel(
            channel_id=str(raw["id"]),
            name=str(raw["name"]),
        )

    def get_messages(
        self,
        channel_id: str,
        limit: int = 10,
        cursor: str | None = None,
    ) -> list[Message]:
        """Retrieve recent messages from a Discord channel.

        Args:
            channel_id: The channel ID to fetch messages from.
            limit: Maximum number of messages to retrieve.
            cursor: Optional pagination cursor (ignored for Discord).

        Returns:
            A list of recent messages ordered oldest to newest.

        """
        url = f"{self._DISCORD_API_BASE}/channels/{channel_id}/messages"
        params: dict[str, str | int] = {"limit": limit}
        if cursor:
            params["before"] = cursor
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
                message_id=f"{channel_id}:{raw['id']!s}",
                channel=channel_id,
                sender=str(
                    raw["author"]["username"]  # type: ignore[index]
                    if isinstance(raw.get("author"), dict)
                    else "unknown"
                ),
                text=str(raw.get("content", "")),
                timestamp=datetime.fromisoformat(
                    str(raw["timestamp"])
                ).replace(tzinfo=UTC),
            )
            for raw in raw_messages
        ]
        return list(reversed(messages))

    def get_message(self, message_id: str) -> Message:
        """Get a single message by its opaque ID.

        Args:
            message_id: Opaque message ID in format 'channel_id:message_id'.

        Returns:
            Message object.

        Raises:
            ValueError: If the message is not found.

        """
        try:
            channel_id, discord_message_id = message_id.split(":", 1)
        except ValueError as exc:
            msg = f"Invalid message_id format: '{message_id}'. Expected 'channel_id:message_id'."
            raise ValueError(msg) from exc

        url = f"{self._DISCORD_API_BASE}/channels/{channel_id}/messages/{discord_message_id}"
        try:
            response = requests.get(url, headers=self._headers, timeout=10)
        except requests.RequestException as exc:
            msg = f"Failed to fetch message: {exc}"
            raise RuntimeError(msg) from exc

        if response.status_code == 404:  # noqa: PLR2004
            msg = f"Message with id '{message_id}' does not exist."
            raise ValueError(msg)

        if not response.ok:
            msg = f"Discord API returned status {response.status_code} fetching message"
            raise RuntimeError(msg)

        raw: dict[str, object] = response.json()
        return Message(
            message_id=f"{channel_id}:{raw['id']}",
            channel=channel_id,
            sender=str(
                raw["author"]["username"]  # type: ignore[index]
                if isinstance(raw.get("author"), dict)
                else "unknown"
            ),
            text=str(raw.get("content", "")),
            timestamp=datetime.fromisoformat(
                str(raw["timestamp"])
            ).replace(tzinfo=UTC),
        )

    def send_message(self, channel_id: str, text: str) -> Message:
        """Send a message to a Discord channel.

        Args:
            channel_id: The channel ID to send to.
            text: The message content.

        Returns:
            The sent message.

        """
        url = f"{self._DISCORD_API_BASE}/channels/{channel_id}/messages"
        payload = {"content": text}
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
            message_id=f"{channel_id}:{raw['id']}",
            channel=channel_id,
            sender=str(
                raw["author"]["username"]  # type: ignore[index]
                if isinstance(raw.get("author"), dict)
                else "unknown"
            ),
            text=str(raw.get("content", "")),
            timestamp=datetime.fromisoformat(
                str(raw["timestamp"])
            ).replace(tzinfo=UTC),
        )

    def delete_message(self, message_id: str) -> None:
        """Delete a message by its opaque ID.

        Args:
            message_id: Opaque message ID in format 'channel_id:message_id'.

        Raises:
            ValueError: If the message cannot be deleted or is not found.

        """
        try:
            channel_id, discord_message_id = message_id.split(":", 1)
        except ValueError as exc:
            msg = f"Invalid message_id format: '{message_id}'. Expected 'channel_id:message_id'."
            raise ValueError(msg) from exc

        url = f"{self._DISCORD_API_BASE}/channels/{channel_id}/messages/{discord_message_id}"
        try:
            response = requests.delete(url, headers=self._headers, timeout=10)
        except requests.RequestException as exc:
            msg = f"Failed to delete message: {exc}"
            raise RuntimeError(msg) from exc

        if response.status_code == 404:  # noqa: PLR2004
            msg = f"Message with id '{message_id}' does not exist."
            raise ValueError(msg)

        if not response.ok:
            msg = f"Discord API returned status {response.status_code} deleting message"
            raise RuntimeError(msg)
