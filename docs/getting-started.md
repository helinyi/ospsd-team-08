# Getting Started

## Prerequisites

- Python 3.13 or higher
- [uv](https://docs.astral.sh/uv/) package manager

---

## Installation

```bash
git clone <repository-url>
cd ospsd-team-08
uv sync --all-packages
```

---

## Environment Variables

Copy `.env.example` to `.env`:
```
DISCORD_BOT_TOKEN=your_bot_token
DISCORD_GUILD_ID=your_guild_id
DISCORD_CLIENT_ID=your_client_id
DISCORD_CLIENT_SECRET=your_client_secret
DISCORD_REDIRECT_URI=http://localhost:8000/auth/callback
SESSION_SECRET_KEY=any-random-string
OPENAI_API_KEY=your_openai_api_key
```
---

## Running Tests

```bash
uv run pytest
```

---

## Running the Service Locally

```bash
uv run uvicorn discord_service.main:app --reload
```

- `http://localhost:8000/health` — health check
- `http://localhost:8000/docs` — API docs
- `http://localhost:8000/auth/login` — Discord OAuth flow
- `http://localhost:8000/calendar/tomorrow` — tomorrow's calendar events
- `http://localhost:8000/metrics` — Prometheus metrics

---

## Deployed Service
```
https://discord-service-122083288286.us-east4.run.app
```
---

## Chat Client Usage

```python
import discord_client_impl
from chat_client_api import get_client

client = get_client()
channels = client.get_channels()
messages = client.get_messages(channels[0].channel_id, limit=10)
client.send_message(channels[0].channel_id, "Hello!")
```

---

## AI Client Usage

```python
import discord_client_impl
from chat_client_api import get_client
from openai_ai_client_impl.client import OpenAIAIClient

ai = OpenAIAIClient(chat_client=get_client())
response = ai.run("What channels are available?")
print(response)
```

---

## Building Documentation

```bash
uv run mkdocs build
uv run mkdocs serve
```