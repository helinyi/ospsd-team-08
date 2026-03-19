# Discord Service API Client

Auto-generated client library for the Discord FastAPI service using [`openapi-python-client`](https://github.com/openapi-generators/openapi-python-client).

## How This Was Generated

This client was generated from the OpenAPI spec of our deployed Cloud Run service (see [CLOUDRUN.md](../../CLOUDRUN.md) for deployment details).

```bash
# Install the generator
uv tool install openapi-python-client

# Generate from the deployed service's OpenAPI spec
cd components
openapi-python-client generate \
  --url https://discord-service-122083288286.us-east4.run.app/openapi.json \
  --output-path discord_service_api_client \
  --overwrite
```

> **Note:** If `ruff` is not found during generation, add it to your PATH:
> ```bash
> PATH="$(find ~/.local/share/uv/tools -name ruff -type f -exec dirname {} \; | head -1):$PATH"
> ```

## Re-generating

If the FastAPI service endpoints change, re-run the generate command above with `--overwrite` and then restore the `[project]` table in `pyproject.toml` (the generator outputs a poetry-only config).

## Usage

```python
from fast_api_client import Client
from fast_api_client.api.default import (
    get_channels_channels_get,
    health_health_get,
    send_channel_message_channels_channel_id_messages_post,
)

client = Client(base_url="https://discord-service-122083288286.us-east4.run.app")

# Health check
with client as c:
    health = health_health_get.sync(client=c)

    # Get channels
    channels = get_channels_channels_get.sync(client=c)

    # Send a message
    from fast_api_client.models import BodySendChannelMessageChannelsChannelIdMessagesPost
    body = BodySendChannelMessageChannelsChannelIdMessagesPost(content="Hello!")
    message = send_channel_message_channels_channel_id_messages_post.sync(
        channel_id="123456",
        client=c,
        body=body,
    )
```

Async usage:

```python
async with client as c:
    channels = await get_channels_channels_get.asyncio(client=c)
```

## API Functions

Each endpoint has four variants:

| Function | Description |
|---|---|
| `sync` | Blocking request, returns parsed data or `None` |
| `sync_detailed` | Blocking request, returns full `Response` object |
| `asyncio` | Async version of `sync` |
| `asyncio_detailed` | Async version of `sync_detailed` |

## Available Endpoints

| Module | Endpoint |
|---|---|
| `health_health_get` | `GET /health` |
| `login_auth_login_get` | `GET /auth/login` |
| `auth_callback_auth_callback_get` | `GET /auth/callback` |
| `get_channels_channels_get` | `GET /channels` |
| `send_channel_message_channels_channel_id_messages_post` | `POST /channels/{channel_id}/messages` |

All endpoint modules are under `fast_api_client.api.default`.
