## Overview

A modular chat client architecture built on Discord with AI tool calling and Google Calendar cross-vertical integration.

## Components

- `chat-client-api` — shared vertical interface (Teams 4, 8, 9)
- `discord_client_impl` — Discord implementation + OAuth 2.0
- `discord_service` — FastAPI microservice on Google Cloud Run
- `openai_ai_client_impl` — AI client with tool calling
- `calendar_integration` — Google Calendar cross-vertical integration

## Live Service
```
https://discord-service-122083288286.us-east4.run.app
```
---

## Quick Links

- [Getting Started](getting-started.md)
- [API Reference](api-reference.md)
- [Discord Implementation](discord-implementation.md)
- [Discord Service](discord-service.md)
- [Service API Client](discord-service-api-client.md)
- [Design Document](DESIGN.md)
- [HW3 Plan](hw3-plan.md)
- [Cloud Run Deployment](CLOUDRUN.md)