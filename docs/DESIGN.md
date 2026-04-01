# DESIGN.md

## Overview

In HW2, we transform the Discord client from a library-based implementation into a service-based architecture.

In HW1, users directly imported `discord_client_impl` and used dependency injection locally. In HW2, we introduce a FastAPI service so that clients communicate with the Discord functionality over HTTP instead of importing the implementation.

This allows multiple programs to reuse a single service without managing Discord credentials or API logic individually.

---

## Architecture Overview

### Components

The system consists of the following components:

1. **chat_client_api**  
   Defines the abstract `ChatClient` interface and data models.

2. **discord_client_impl**  
   Implements the interface using the real Discord API and handles OAuth.

3. **discord_service (FastAPI)**  
   Exposes the implementation through HTTP endpoints.

4. **discord_service_api_client**  
   Auto-generated client from the OpenAPI specification.

5. **Adapter Layer**  
   Wraps the generated API client and presents the same interface as `ChatClient`.

---

### Request Flow

A complete request flows as follows:

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


Explanation:

1. User code calls methods defined in `ChatClient`
2. The adapter translates method calls into API client calls  
3. The generated client sends HTTP requests to the FastAPI service  
4. The service calls the underlying `DiscordClient`  
5. The implementation interacts with the Discord API  
6. The response is returned as JSON back through the layers  

---

### Sample API Response

Example response from:

`GET /health`

```json
{
  "status": "ok"
}
```

------------------------------------------------------------------------

## API Design

### Endpoints

-   GET /health\
-   GET /auth/login\
-   GET /auth/callback\
-   GET /users/me\
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

The generated API client is based on HTTP requests and does not match the original ChatClient interface (which uses method calls).

To ensure that user code remains unchanged between HW1 and HW2, an adapter layer is introduced to bridge this gap.

### How It Works

The adapter wraps the generated API client and exposes the same interface as ChatClient

### Example Comparison

Library (HW1):

```python
import discord_client_impl
from chat_client_api import get_client

client = get_client()
client.send_message("123", "Hello")
```

Service (HW2):
```python
from chat_client_api import get_client
import discord_client_adapter

client = get_client()
client.send_message("123", "Hello")
```

Internally, the adapter translates this call into:

```python
send_message.sync(
    client=api_client,
    channel_id="123",
    body={"content": "Hello"}
)
```

------------------------------------------------------------------------

## Testing Strategy

### What We Tested

We tested four main parts of the system:

1. **discord_client_impl**  
   We tested this component because it contains the core business logic and is the layer that directly communicates with the Discord API.

2. **discord_service**  
   We tested the FastAPI service because it is the bridge between HTTP requests and the original implementation. We needed to verify that requests, responses, and status codes were handled correctly.

3. **discord_service_api_client**  
   We tested the generated API client because it is the main way user-facing code communicates with the deployed service in HW2.

4. **Adapter behavior**  
   We tested adapter-level behavior to ensure that service-based usage remained consistent with the original `ChatClient` interface.

### Test Types

We used a mix of **unit, integration, and end-to-end tests**:

- **Unit tests** were used for `discord_client_impl` because we wanted to verify the client logic in isolation without depending on the real Discord API.
- **Integration tests** were used to verify that the generated client, dependency injection, and service wiring worked correctly together.
- **End-to-end tests** were used to validate the full request path against the real deployed service, because this is the best way to confirm that the complete HW2 architecture works in practice.

### Mocking Strategy

We mocked the following in tests:

- **Discord API responses** were mocked in unit tests so that tests would be deterministic, fast, and not depend on external network calls.
- **Environment variables and credentials** were mocked so that tests could run safely without requiring real secrets.

We used **real implementations** in end-to-end tests, where requests were sent through the real service and, when configured, reached the actual Discord API. This was important because it verified the real deployment behavior instead of only isolated local behavior.

### Interface Compliance

We verified interface compliance in two ways.

First, we used a **testing approach**:
- integration tests checked that the object returned by `get_client()` behaved like the expected client implementation
- adapter/service-facing calls were tested to make sure the expected methods (`get_channels`, `get_messages`, `send_message`) worked correctly

Second, we ensured **compliance by design**:
- the adapter layer was written to preserve the same interface expected by `chat_client_api`
- return values were checked against the expected models such as `Channel` and `Message`

Together, this ensured that users could continue interacting with the system through the same high-level client contract, even though the backend was now service-based.

------------------------------------------------------------------------

## Summary

-   Added FastAPI service\
-   Generated OpenAPI client\
-   Enabled remote access\
-   Improved scalability
