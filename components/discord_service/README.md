# discord_service

## Purpose

`discord_service` exposes the `discord_client_impl` functionality over HTTP as a FastAPI microservice.

This component acts as the **deployment unit** of the architecture — it wraps the core Discord client logic and makes it accessible as a publicly reachable REST API with OAuth 2.0 authentication.

---

## Architecture Role

This component represents the **Service Component**.

It:
- Imports and uses `discord_client_impl` to interact with Discord
- Exposes HTTP endpoints matching the `ChatClient` interface
- Implements OAuth 2.0 Authorization Code Flow for user authentication
- Stores OAuth tokens securely in server-side sessions
- Is deployed to Google Cloud Run with automatic deployments via CircleCI

---

## Live Deployment

Service is live at:
```
https://discord-service-122083288286.us-east4.run.app
```

API documentation available at:
```
https://discord-service-122083288286.us-east4.run.app/docs
```

---

## Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Health check |
| `GET` | `/auth/login` | Redirects to Discord OAuth2 login |
| `GET` | `/auth/callback` | Handles OAuth2 callback and stores token |
| `GET` | `/users/me` | Returns authenticated user info |
| `GET` | `/channels` | Returns all text channels in the guild |
| `GET` | `/channels/{channel_id}/messages` | Returns recent messages from a channel |
| `POST` | `/channels/{channel_id}/messages` | Sends a message to a channel |

---

## OAuth 2.0 Flow

1. User visits `/auth/login` → redirected to Discord authorization page
2. User logs in and clicks "Authorize"
3. Discord redirects to `/auth/callback` with a temporary code
4. Service exchanges code for an access token
5. Access token stored in server-side session cookie
6. User can now call `/users/me` to verify their identity

---

## Required Environment Variables

| Variable | Description |
|---|---|
| `DISCORD_BOT_TOKEN` | Bot token from Discord Developer Portal |
| `DISCORD_GUILD_ID` | ID of the Discord server to operate on |
| `DISCORD_CLIENT_ID` | OAuth2 Client ID from Discord Developer Portal |
| `DISCORD_CLIENT_SECRET` | OAuth2 Client Secret from Discord Developer Portal |
| `DISCORD_REDIRECT_URI` | OAuth2 redirect URI |
| `SESSION_SECRET_KEY` | Secret key for signing session cookies |

---

## Local Development

Copy `.env.example` to `.env` and fill in your credentials:
```
DISCORD_BOT_TOKEN=your_bot_token
DISCORD_GUILD_ID=your_guild_id
DISCORD_CLIENT_ID=your_client_id
DISCORD_CLIENT_SECRET=your_client_secret
DISCORD_REDIRECT_URI=http://localhost:8000/auth/callback
SESSION_SECRET_KEY=any-random-string
```

Install dependencies and start the service:
```bash
uv sync --all-packages
uv run uvicorn discord_service.main:app --reload
```

---

## Dependencies

- `chat_client_api`
- `discord_client_impl`
- `fastapi`
- `uvicorn`
- `python-dotenv`
- `starlette`
- `itsdangerous`
