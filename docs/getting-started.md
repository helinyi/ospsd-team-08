# Getting Started

## Prerequisites

- Python 3.10 or higher
- [uv](https://docs.astral.sh/uv/) package manager
- (Optional) Docker (for containerized deployment)

---

## Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd opssd-team-08
```

2. Install dependencies:

```bash
uv sync --all-packages
```

---

## Running Tests

Run all tests:

```bash
uv run pytest
```

This includes:

- Unit tests (mocked Discord API)
- Integration tests (API client)
- E2E tests (real service, may skip if not configured)

---

## Running the Discord Service (FastAPI)

Start the service locally:

```bash
uv run uvicorn discord_service.main:app --reload
```

The service will be available at:

- API base: http://127.0.0.1:8000
- OpenAPI spec: http://127.0.0.1:8000/openapi.json
- Docs UI: http://127.0.0.1:8000/docs

---

## Deployed Service

The service is deployed on Google Cloud Run:

https://discord-service-122083288286.us-east4.run.app

You can verify:

```bash
curl https://discord-service-122083288286.us-east4.run.app/health
```

Expected response:

```json
{"status":"ok"}
```

---

## Using the Chat Client (Local Implementation)

```python
import discord_client_impl
from chat_client_api import get_client

client = get_client()

channels = client.get_channels()
messages = client.get_messages("channel_id")

client.send_message("channel_id", "Hello!")
```

---

## Using the Service via API Client

The `discord_service_api_client` is generated from OpenAPI and can be used to call the deployed service.

Example usage:

```python
from discord_service_api_client import Client
from discord_service_api_client.api.default import get_channels_channels_get

client = Client(base_url="https://discord-service-122083288286.us-east4.run.app")

response = get_channels_channels_get.sync(client=client)
print(response)
```

---

## Dependency Injection

This project uses a simple dependency injection pattern.

- `chat_client_api` defines the interface
- `discord_client_impl` registers a concrete implementation

Usage:

```python
import discord_client_impl
from chat_client_api import get_client

client = get_client()
```

If no implementation is registered, `get_client()` will raise a `RuntimeError`.

---

## Environment Variables

The following environment variables are required for Discord OAuth:

- DISCORD_CLIENT_ID
- DISCORD_CLIENT_SECRET
- DISCORD_REDIRECT_URI
- DISCORD_BOT_TOKEN
- DISCORD_GUILD_ID

In production:
- Stored securely via Cloud Run (not in source control)

---

## OpenAPI Client Generation

The API client is generated from:

https://discord-service-122083288286.us-east4.run.app/openapi.json

Using:

```bash
openapi-python-client generate --url <openapi.json>
```

---

## Building Documentation

To build documentation:

```bash
uv run mkdocs build
```

To preview locally:

```bash
uv run mkdocs serve
```

Then open:

http://127.0.0.1:8000
