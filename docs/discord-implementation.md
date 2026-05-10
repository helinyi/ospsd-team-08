# Discord Implementation

This document describes the Discord-based implementation of the shared chat vertical API.

## Component Overview

- **Interface:** shared `chat-client-api` (external git dependency)
  - Defines the `ChatClient` contract and `Channel` / `Message` models.
  - Provides `register_client(...)` and `get_client()` for dependency injection.
  - Shared across Teams 4 (Telegram), 8 (Discord), and 9 (Slack).

- **Implementation:** `components/discord_client_impl`
  - Implements all 6 `ChatClient` methods using real Discord API calls.
  - Handles both bot token authentication and OAuth 2.0 Authorization Code Flow.
  - Registers itself via a factory hook so consumers only depend on `chat_client_api`.

- **Service:** `components/discord_service`
  - Exposes `discord_client_impl` over HTTP as a FastAPI microservice.
  - Implements OAuth 2.0 endpoints for user authentication.
  - Includes Google Calendar cross-vertical endpoints.
  - Deployed to Google Cloud Run at `https://discord-service-122083288286.us-east4.run.app`

## Dependency Injection

```python
import discord_client_impl
from chat_client_api import get_client

client = get_client()
```

## Mapping Interface Methods to Discord

| Method | Discord API Call | Notes |
|---|---|---|
| `get_channels()` | `GET /guilds/{guild_id}/channels` | Returns text channels only |
| `get_channel(channel_id)` | `GET /channels/{channel_id}` | Single channel lookup |
| `get_messages(channel_id, limit, cursor)` | `GET /channels/{channel_id}/messages` | Oldest first, cursor maps to `before` |
| `get_message(message_id)` | Fetches via `get_messages` | `message_id` encoded as `"channel_id:discord_message_id"` |
| `send_message(channel_id, text)` | `POST /channels/{channel_id}/messages` | Returns created message |
| `delete_message(message_id)` | `DELETE /channels/{channel_id}/messages/{id}` | Splits opaque ID to get both IDs |

## Authentication

### Bot Token Authentication
Reads `DISCORD_BOT_TOKEN` from environment and builds `Authorization: Bot <token>` headers.

### OAuth 2.0 Authorization Code Flow
1. `get_authorization_url()` — generates Discord login URL
2. User logs in and authorizes on Discord
3. Discord redirects to `/auth/callback` with authorization code
4. `exchange_code()` — exchanges code for access token
5. Token stored in server-side session
6. `get_oauth_headers()` — builds `Authorization: Bearer <token>` headers

### Required Environment Variables

| Variable | Description |
|---|---|
| `DISCORD_BOT_TOKEN` | Bot token for guild/channel operations |
| `DISCORD_GUILD_ID` | Target Discord server ID |
| `DISCORD_CLIENT_ID` | OAuth2 Client ID |
| `DISCORD_CLIENT_SECRET` | OAuth2 Client Secret |
| `DISCORD_REDIRECT_URI` | OAuth2 callback URL |
| `SESSION_SECRET_KEY` | Secret key for signing session cookies |
| `OPENAI_API_KEY` | OpenAI API key for AI client |
| `GOOGLE_OAUTH_CREDENTIALS_PATH` | Path to Google OAuth credentials file |
| `GOOGLE_OAUTH_TOKEN_PATH` | Path to Google OAuth token file |
| `GOOGLE_CALENDAR_ID` | Google Calendar ID (default: primary) |

## Error Handling

- Network errors raise `RuntimeError` with descriptive messages
- Non-200 API responses raise `RuntimeError` with status code
- FastAPI service converts these to HTTP status codes (502, 404, 401, 503)

## Testing

- Unit tests mock all Discord API calls
- Integration tests verify DI factory injection
- E2E tests run against real Discord infrastructure, skipped when credentials unavailable
- Coverage threshold: 90%, enforced in CI