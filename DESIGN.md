# DESIGN.md

## Overview

This project implements a modular chat client architecture built on Discord, evolving across three homework sprints:

- **HW1**: Direct library-based Discord client with OAuth 2.0
- **HW2**: FastAPI microservice with auto-generated client and adapter pattern
- **HW3**: Shared vertical API alignment, AI client integration, Google Calendar cross-vertical integration, Prometheus telemetry, and Terraform IaC

For the HW3 shared vertical API adaptation plan, see [hw3-plan.md](hw3-plan.md).

---

## Architecture Overview

### Components

1. **chat-client-api** (shared vertical, external git dep)
   Abstract `ChatClient` interface and data models (`Channel`, `Message`) agreed upon by Teams 4, 8, and 9.

2. **discord_client_impl**
   Implements `ChatClient` using real Discord API calls. Handles bot token auth and OAuth 2.0.

3. **discord_service (FastAPI)**
   Exposes Discord functionality over HTTP. Also wires in AI and calendar cross-vertical endpoints.

4. **discord_service_api_client**
   Auto-generated HTTP client from the OpenAPI spec.

5. **chat_client_adapter**
   Wraps the generated API client and presents the same `ChatClient` interface.

6. **ai_client_api**
   Abstract interface for AI clients. Framework-free, no provider SDK leakage.

7. **openai_ai_client_impl**
   Concrete AI client using OpenAI GPT-4o-mini with tool calling wired to Discord and Google Calendar domain actions. Registers itself via register_client() on import.

8. **calendar_integration**
   Formats Google Calendar events into chat-friendly messages.

9. **google_calendar_adapter**
   Implements the shared `calendar-client-api` interface using the real Google Calendar API. Tests mock the Google API service object — no real credentials needed for unit tests.

---

### Request Flow

A complete request flows as follows:
#### Chat Flow
```
User Code
↓
Adapter
↓
Generated API Client
↓
FastAPI Service
↓
DiscordClient (Implementation)
↓
Discord API
↓
Response (JSON)
```
#### AI Tool-Calling Flow
```
User prompt
↓
OpenAIAIClient.run()
↓
Tool calling loop (max 5 iterations, raises ToolLoopExhaustedError if exceeded)
↓
Tool handlers → ChatClient methods (get_channels, get_messages, send_message)
OR CalendarClient methods (create_calendar_event, schedule_meeting_for_message)
↓
Discord API / Google Calendar API
↓
AI response returned to user
↓
prometheus_fastapi_instrumentator records latency + status [telemetry]
```
#### Cross-Vertical Calendar Flow
```
GET /calendar/tomorrow
↓
google_calendar_adapter → Google Calendar API
↓
calendar_integration formats events
↓
Formatted message returned
```

## End-to-End Request Flow

```
User prompt (e.g. "Schedule a meeting for the message about the project")
↓
OpenAIAIClient.run()                          [AI loop]
↓
Tool calling → schedule_meeting_for_message() [tool dispatch]
↓
chat_client.get_message()                     [fetch Discord message]
↓
google_calendar_adapter.create_event()        [cross-vertical call]
↓
Google Calendar API
↓
AI response returned to user
↓
prometheus_fastapi_instrumentator records latency + status  [telemetry]
↓
Grafana dashboard visualizes metrics
```
## Shared Vertical API (HW3)

In HW3, the local `chat_client_api` package was replaced with the shared vertical API agreed upon by Teams 4 (Telegram), 8 (Discord), and 9 (Slack). Consumed as a `uv` git dependency:

```toml
chat-client-api = { git = "https://github.com/HarshithKoriRaj/Shared-API.git" }
```

Vertical contract (memo): [ospsd-chat-api — Teams 4, 8, 9](https://github.com/HarshithKoriRaj/Shared-API/blob/main/README.md)

The shared interface defines 6 methods:
- `get_channels() -> list[Channel]`
- `get_channel(channel_id: str) -> Channel`
- `get_messages(channel_id: str, limit: int, cursor: str | None) -> list[Message]`
- `get_message(message_id: str) -> Message`
- `send_message(channel_id: str, text: str) -> Message`
- `delete_message(message_id: str) -> None`

---

## AI Integration (HW3)

`ai_client_api` defines the abstract interface and provides `register_client()` and `get_client()` following the same DI pattern as `chat_client_api`:

```python
class AIClient(ABC):
    @abstractmethod
    def run(self, user_input: str, context: dict[str, Any] | None = None) -> str: ...
```

Importing `openai_ai_client_impl` automatically registers the OpenAI implementation:

```python
import openai_ai_client_impl  # registers OpenAI as the AI client
from ai_client_api import get_client

ai = get_client()
response = ai.run("What channels are available?")
```

`openai_ai_client_impl` implements this using OpenAI GPT-4o-mini with a tool-calling loop.

| Tool | Action |
|---|---|
| `get_channels` | Lists all Discord channels |
| `get_channel` | Gets a specific channel by ID |
| `get_messages` | Fetches recent messages from a channel |
| `send_message` | Sends a message to a channel |
| `create_calendar_event` | Creates a Google Calendar event from user-provided parameters |
| `schedule_meeting_for_message` | Fetches a Discord message and schedules a calendar meeting using the message content as description|

Credentials are loaded from `OPENAI_API_KEY` environment variable — never hardcoded.

---

## Cross-Vertical Integration (HW3)

Google Calendar (Team 5) is integrated via their shared `calendar-client-api`:

```toml
calendar-client-api = { git = "https://github.com/samuelj25/ospsd-team-05", subdirectory = "components/calendar_client_api" }
```

Two endpoints are exposed in `discord_service`:
- `GET /calendar/tomorrow` — returns tomorrow's calendar events as a formatted message
- `GET /calendar/events?start_time=...&end_time=...` — returns events for a given time range

The AI client also integrates directly with the calendar vertical via two tools:
- `create_calendar_event` — creates a calendar event from parameters provided by the user
- `schedule_meeting_for_message` — fetches a Discord message by ID and uses its content to create a calendar meeting, demonstrating true cross-vertical AI tool-calling
---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Health check |
| GET | `/auth/login` | Discord OAuth2 login |
| GET | `/auth/callback` | OAuth2 callback |
| GET | `/users/me` | Authenticated user info |
| GET | `/channels` | List all channels |
| GET | `/channels/{id}/messages` | Get recent messages |
| POST | `/channels/{id}/messages` | Send a message |
| GET | `/calendar/tomorrow` | Tomorrow's calendar events |
| GET | `/calendar/events` | Events for a time range |
| GET | `/metrics` | Prometheus metrics |
| POST | `/ai/chat` | AI-powered chat with tool calling |
---

## Observability (HW3)

Request latency, success rate, and failure rate are instrumented via `prometheus_fastapi_instrumentator`. Metrics are exposed at `/metrics` and visualized in a Grafana dashboard showing:
- Request latency per endpoint
- Success rate (2xx responses)
- Failure rate (4xx/5xx responses)

> **Note:** `/metrics` is exposed publicly by default via `prometheus_fastapi_instrumentator`. This is acceptable for grading purposes, but in production the metrics endpoint should be protected behind a private path, API token, or IAM allowlist to prevent exposing internal service telemetry.


Metrics are visualized in a Grafana Cloud dashboard at:
[https://aw3950.grafana.net/public-dashboards/11a16d893f7e4302acfaf12feda6a33e](https://aw3950.grafana.net/public-dashboards/11a16d893f7e4302acfaf12feda6a33e)

---

## Infrastructure as Code (HW3)

Terraform configuration lives in `infra/terraform/` and provisions:
- Google Cloud Run service
- Environment variables and secrets
- IAM bindings

---

## Error Handling

| Status | Meaning |
|---|---|
| 404 | Channel or resource not found |
| 400 | Bad request or OAuth error |
| 401 | Not authenticated |
| 502 | Discord or external API error |
| 503 | Calendar credentials not configured |

---

## Testing Strategy

### Test Types

- **Unit tests** — each component has isolated tests mocking external APIs
- **Integration tests** — verify DI wiring, AI tool-calling pipeline, and cross-vertical integration
- **E2E tests** — validate full request path against real deployed service

### Coverage

Coverage threshold of 90% is enforced in CI via `pytest-cov`.

### Mocking Strategy

- Discord API responses mocked in unit tests for determinism
- OpenAI SDK mocked in AI client tests — no real API calls
- Calendar client mocked in service tests using `FakeCalendarClient`
- Real implementations used in E2E tests against the deployed service

---

## Deployment

Service is deployed on Google Cloud Run:
```
https://discord-service-122083288286.us-east4.run.app
```

API docs available at:
```
https://discord-service-122083288286.us-east4.run.app/docs
```

For Cloud Run setup and bootstrap instructions, see [CLOUDRUN.md](CLOUDRUN.md).