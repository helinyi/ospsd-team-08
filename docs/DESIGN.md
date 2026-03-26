# DESIGN.md

## Overview

In HW2, we transform the Discord client from a library-based
implementation into a service-based architecture.

In HW1, users directly imported `discord_client_impl` and used
dependency injection locally. In HW2, we introduce a FastAPI service so
that clients communicate with the Discord functionality over HTTP
instead of importing the implementation.

This allows multiple programs to reuse a single service without managing
Discord credentials or API logic individually.

------------------------------------------------------------------------

## Architecture Overview

### Components

The system consists of the following components:

1.  chat_client_api\
    Defines the abstract ChatClient interface and data models.

2.  discord_client_impl\
    Implements the interface using the real Discord API and handles
    OAuth.

3.  discord_service (FastAPI)\
    Exposes the implementation through HTTP endpoints.

4.  discord_service_api_client\
    Auto-generated client from the OpenAPI specification of the service.

------------------------------------------------------------------------

### Request Flow

User Code → API Client → FastAPI Service → DiscordClient → Discord API →
Response

------------------------------------------------------------------------

### Sample API Response

GET /health

{ "status": "ok" }

------------------------------------------------------------------------

## API Design

### Endpoints

-   GET /health\
-   GET /auth/login\
-   GET /auth/callback\
-   GET /channels\
-   GET /channels/{channel_id}/messages\
-   POST /channels/{channel_id}/messages

------------------------------------------------------------------------

### Error Handling

-   404 Not Found → invalid channel\
-   400 Bad Request → OAuth error\
-   502 Bad Gateway → Discord API error

Example:

{ "detail": "Channel with ID not found" }

------------------------------------------------------------------------

## The Adapter Pattern

### Why It's Needed

The generated API client does not match the original ChatClient
interface exactly, since it uses HTTP requests.

------------------------------------------------------------------------

### Example Comparison

Library (HW1):

import discord_client_impl from chat_client_api import get_client

client = get_client() client.send_message("123", "Hello")

Service (HW2):

from discord_service_api_client import Client from
discord_service_api_client.api.default import send_message

client = Client(base_url="http://localhost:8000")
send_message.sync(client=client, channel_id="123", body={"content":
"Hello"})

------------------------------------------------------------------------

## Testing Strategy

### What We Tested

-   Discord client implementation\
-   FastAPI service endpoints\
-   API client integration

------------------------------------------------------------------------

### Test Types

-   Unit tests (mock Discord API)\
-   Integration tests\
-   End-to-end tests

------------------------------------------------------------------------

### Mocking Strategy

-   Mock Discord API\
-   Mock environment variables\
-   Real API only in E2E

------------------------------------------------------------------------

### Interface Compliance

-   Verify outputs match expected models\
-   Use typed models\
-   Ensure consistent behavior

------------------------------------------------------------------------

## Summary

-   Added FastAPI service\
-   Generated OpenAPI client\
-   Enabled remote access\
-   Improved scalability
