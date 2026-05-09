# Discord Service

`discord_service` is the FastAPI microservice that exposes Discord functionality over HTTP and wires in AI and calendar cross-vertical endpoints.

## Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Returns `{"status": "ok"}` |
| GET | `/auth/login` | Redirects to Discord OAuth authorization |
| GET | `/auth/callback` | Exchanges code for access token |
| GET | `/users/me` | Returns authenticated Discord user info |
| GET | `/channels` | Lists all text channels |
| GET | `/channels/{channel_id}/messages` | Returns recent messages |
| POST | `/channels/{channel_id}/messages` | Sends a message |
| GET | `/calendar/tomorrow` | Returns tomorrow's Google Calendar events |
| GET | `/calendar/events` | Returns events for a given time range |
| GET | `/metrics` | Prometheus telemetry metrics |

## Dependency Injection

- `get_client()` — provides a `ChatClient` instance
- `get_oauth_handler()` — provides a `DiscordOAuthHandler`
- `get_calendar_client()` — provides a `CalendarClient` instance

## Error Handling

| Status | Meaning |
|---|---|
| 404 | Channel not found |
| 400 | OAuth exchange failure |
| 401 | Not authenticated |
| 502 | Discord or external API error |
| 503 | Calendar credentials not configured |
| 422 | Missing or invalid request parameters |