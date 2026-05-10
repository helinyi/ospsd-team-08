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
### Google Calendar Setup

To enable `/calendar/*` endpoints locally:

```bash
gcloud auth login  # one time per machine
bash scripts/dev-setup-calendar.sh  # writes credentials.json + token.json
```

Both files are gitignored. Without this step, only `/calendar/*` returns 503 — all other endpoints work normally.

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
- `http://localhost:8000/auth/callback` — OAuth callback
- `http://localhost:8000/users/me` — authenticated Discord user info
- `http://localhost:8000/channels` — list all channels
- `http://localhost:8000/channels/{channel_id}/messages` — get recent messages
- `http://localhost:8000/calendar/tomorrow` — tomorrow's calendar events
- `http://localhost:8000/calendar/events` — events for a time range
- `http://localhost:8000/ai/chat` — AI-powered chat with tool calling
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
import discord_client_impl       # registers Discord as chat client
import openai_ai_client_impl     # registers OpenAI as AI client
from ai_client_api import get_client

ai = get_client()
response = ai.run("What channels are available?")
print(response)
```

---

## Telemetry
Live Grafana dashboard: [https://aw3950.grafana.net/public-dashboards/11a16d893f7e4302acfaf12feda6a33e](https://aw3950.grafana.net/public-dashboards/11a16d893f7e4302acfaf12feda6a33e)

---

## Building Documentation

```bash
uv run mkdocs build
uv run mkdocs serve
```