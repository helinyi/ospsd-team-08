# Discord Service API Client

`discord_service_api_client` is the component reserved for OpenAPI-generated client code from `discord_service`.

## Generation Workflow

1. Start the FastAPI service (locally or via deployed service).
2. Generate client code from `/openapi.json`.
3. Use the stable wrapper module (`discord_service_api_client.client`) as the adapter-facing surface.

## Current Endpoints

- `GET /health`
- `GET /auth/login`
- `GET /auth/callback`
- `GET /channels`
- `POST /channels/{channel_id}/messages`
- `GET /channels/{channel_id}/messages`

## Scaffold Status

- Wrapper client exists with typed method signatures.
- Endpoint wrappers are generated under `api/default/`.
- Request and response models are generated under `models/`.
- Runtime usage depends on configured base URL of deployed service.
- Intended to be used by the adapter layer for remote service calls.