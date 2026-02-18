# Discord Implementation

This document describes the Discord-based implementation of the `chat_client_api` interface.

## Component Overview

- **Interface:** `components/chat_client_api`
  - Defines the `ChatClient` contract and the `Channel` / `Message` models.
  - Provides `register_client_factory(...)` and `get_client()` for dependency injection.

- **Implementation:** `components/discord_client_impl`
  - Implements the `ChatClient` interface using Discord as the backing provider.
  - Registers itself via a factory hook so that consumers only depend on `chat_client_api`.

## Dependency Injection

The implementation uses a factory-based dependency injection pattern:

1. Importing `discord_client_impl` registers a `ChatClient` factory.
2. Calling `chat_client_api.get_client()` returns a concrete Discord client instance.
3. If no implementation is imported, `get_client()` raises an error.

Example:

```python
import discord_client_impl
from chat_client_api import get_client

client = get_client()
```

## Mapping Interface Methods to Discord

The Discord client provides concrete behavior for the `ChatClient` methods:

- `get_channels()`
  - Returns a list of accessible Discord channels, mapped into `Channel` models.

- `get_messages(channel_id, limit=10)`
  - Fetches recent messages for a channel and maps them into `Message` models.

- `send_message(channel_id, content)`
  - Sends a message to the target channel and returns the created `Message`.

All provider-specific types remain internal to `discord_client_impl`. The public surface
only exposes `chat_client_api` models.

## Authentication / Configuration

The Discord implementation authenticates using environment-based configuration.

Typical configuration includes:

- A bot token (e.g., `DISCORD_BOT_TOKEN`)
- Optional identifiers for integration/E2E tests (e.g., a channel id)

These values are read at runtime by the implementation and are not required by the interface.

## Error Handling

Provider-specific errors are handled inside `discord_client_impl`.

The goal is to avoid leaking Discord-specific exceptions into the interface layer. When possible,
errors are surfaced in a consistent way (e.g., through controlled exceptions or clear failure modes).

## Testing Notes

- **Unit tests** should mock network/provider calls and validate mapping logic.
- **Integration tests** should verify that importing `discord_client_impl` correctly injects the factory.
- **E2E tests** (when enabled) should run against real Discord infrastructure using environment variables.

## Design Goals

- Keep the interface provider-agnostic.
- Avoid leaking Discord SDK types into `chat_client_api`.
- Make the implementation swappable via dependency injection.
- Keep the interface “deep”: small surface area with meaningful capability underneath.
