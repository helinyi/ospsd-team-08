# Discord Service API Client

`discord_service_api_client` is the auto-generated OpenAPI client for `discord_service`.

## Generation Workflow

1. Start the FastAPI service locally or use the deployed service.
2. Generate client from `/openapi.json`:
```bash
openapi-python-client generate --url https://discord-service-122083288286.us-east4.run.app/openapi.json
```

## Current Endpoints

- `GET /health`
- `GET /auth/login`
- `GET /auth/callback`
- `GET /channels`
- `GET /channels/{channel_id}/messages`
- `POST /channels/{channel_id}/messages`

## Usage

```python
from fast_api_client import Client
from fast_api_client.api.default import get_channels_channels_get

client = Client(base_url="https://discord-service-122083288286.us-east4.run.app")
response = get_channels_channels_get.sync(client=client)
print(response)
```