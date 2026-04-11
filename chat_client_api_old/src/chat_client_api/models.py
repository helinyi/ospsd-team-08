"""Data models for the Chat Client API."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime  # noqa: TC003


@dataclass(frozen=True)
class Channel:
    """Represents a chat channel or conversation."""

    id: str
    name: str
    topic: str | None = None


@dataclass(frozen=True)
class Message:
    """Represents a chat message."""

    id: str
    channel: Channel
    sender: str
    content: str
    timestamp: datetime
