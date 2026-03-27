# Discord Implementation

This document describes the Discord-based implementation of the `chat_client_api` interface.

## Component Overview

- **Interface:** `components/chat_client_api`
  - Defines the `ChatClient` contract and the `Channel` / `Message` models.
  - Provides `register_client_factory(...)` and `get_client()` for dependency injection.

- **Implementation:** `components/discord_client_impl`
  - Implements the `ChatClient` interface using real Discord API calls.
  - Handles both bot token authentication and OAuth 2.0 Authorization Code Flow.
  - Registers itself via a factory hook so that consumers only depend on `chat_client_api`.

- **Service:** `components/discord_service`
  - Exposes `discord_client_impl` over HTTP as a FastAPI microservice.
  - Implements OAuth 2.0 endpoints for user authentication.
  - Deployed to Google Cloud Run at `https://discord-service-122083288286.us-east4.run.app`

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

The Discord client provides concrete behavior for the `ChatClient` methods by making real HTTP calls to Discord's API:

- `get_channels()`
  - Calls `GET /guilds/{guild_id}/channels` and returns text channels (type=0) mapped into `Channel` models.

- `get_messages(channel, limit=10)`
  - Calls `GET /channels/{channel_id}/messages` and maps responses into `Message` models.
  - Returns messages ordered oldest to newest (Discord returns newest first).

- `send_message(channel, content)`
  - Calls `POST /channels/{channel_id}/messages` and returns the created `Message`.

All provider-specific types remain internal to `discord_client_impl`. The public surface
only exposes `chat_client_api` models.

## Authentication

### Bot Token Authentication
Used for all guild and channel operations. The `DiscordAuthenticator` class reads `DISCORD_BOT_TOKEN` from environment variables and builds the required `Authorization: Bot <token>` headers.

### OAuth 2.0 Authorization Code Flow
Used for user identity. The `DiscordOAuthHandler` class implements the full OAuth 2.0 flow:

1. `get_authorization_url()` — generates the Discord login URL with required scopes
2. User logs in and authorizes the application on Discord
3. Discord redirects to `/auth/callback` with a temporary authorization code
4. `exchange_code()` — exchanges the code for an access token via a server-to-server request
5. Access token stored in server-side session for subsequent requests
6. `get_oauth_headers()` — builds `Authorization: Bearer <token>` headers for user-level API calls

### Required Environment Variables

| Variable | Description |
|---|---|
| `DISCORD_BOT_TOKEN` | Bot token for guild/channel operations |
| `DISCORD_GUILD_ID` | Target Discord server ID |
| `DISCORD_CLIENT_ID` | OAuth2 Client ID |
| `DISCORD_CLIENT_SECRET` | OAuth2 Client Secret |
| `DISCORD_REDIRECT_URI` | OAuth2 callback URL |
| `SESSION_SECRET_KEY` | Secret key for signing session cookies |

## Error Handling

Provider-specific errors are handled inside `discord_client_impl`.

The goal is to avoid leaking Discord-specific exceptions into the interface layer. When possible,
errors are surfaced in a consistent way:

- Network errors raise `RuntimeError` with descriptive messages
- Non-200 API responses raise `RuntimeError` with the status code
- The FastAPI service converts these to appropriate HTTP status codes (502, 404, 401)

## Testing Notes

- **Unit tests** mock all Discord API calls using `unittest.mock` and validate mapping logic.
- **Integration tests** verify that importing `discord_client_impl` correctly injects the factory.
- **E2E tests** run against real Discord infrastructure using environment variables — skipped gracefully when credentials are unavailable.
- Coverage threshold is set to 90% and enforced in CI.

## Design Goals

- Keep the interface provider-agnostic.
- Avoid leaking Discord SDK types into `chat_client_api`.
- Make the implementation swappable via dependency injection.
- Keep the interface "deep": small surface area with meaningful capability underneath.
- OAuth 2.0 identifies users while bot token handles guild operations — matching Discord's API design.