# Discord Service

`discord_service` is the HW2 FastAPI deployment unit.

## Current Endpoints

- `GET /health`
- `GET /auth/login`
- `GET /auth/callback`
- `GET /channels`
- `POST /channels/{channel_id}/messages`
- `GET /channels/{channel_id}/messages`

## Endpoint Behavior

- `/health`
  - Returns service status
  - Response: `{"status": "ok"}`

- `/auth/login`
  - Redirects the user to Discord OAuth authorization URL

- `/auth/callback`
  - Exchanges authorization code for access token
  - Returns:
    ```json
    {
      "access_token": "...",
      "token_type": "Bearer"
    }
    ```

- `/channels`
  - Returns a list of channels from the Discord client

- `/channels/{channel_id}/messages` (POST)
  - Sends a message to a specific channel
  - Request body:
    ```json
    {
      "content": "message text"
    }
    ```

- `/channels/{channel_id}/messages` (GET)
  - Retrieves recent messages from a channel
  - Query parameter:
    - `limit` (default 10, max 100)

## Dependency Injection

The service uses FastAPI dependency injection:

- `get_client()` provides a `DiscordClient`
- `get_oauth_handler()` provides a `DiscordOAuthHandler`

This allows tests to override dependencies and mock external API behavior.

## Error Handling

- Invalid channel → `404 Not Found`
- OAuth exchange failure → `400 Bad Request`
- Discord API/runtime failure → `502 Bad Gateway`
- Missing required parameters → `422 Unprocessable Entity`

## Notes

- OAuth flow is fully implemented using Authorization Code Flow
- All endpoints are backed by the real Discord API via `DiscordClient`
- Service is designed to be deployed and accessed remotely
- OpenAPI specification is available at `/openapi.json`