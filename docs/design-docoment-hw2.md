# Design Document – HW2

## Overview

In HW2, we extend the chat client system by replacing the in-memory Discord client implementation with a real Discord API integration. This includes introducing a FastAPI-based service layer, generating an OpenAPI client, and supporting OAuth 2.0 authentication.

The architecture follows a service-oriented design where the Discord functionality is exposed through HTTP endpoints and consumed via a generated API client.

---

## Components

### 1. discord_client_impl

This component provides a concrete implementation of the chat client interface using the real Discord API.

Key features:
- Replaces the in-memory stub with real HTTP calls to Discord API
- Supports core operations:
  - `get_channels`
  - `get_messages`
  - `send_message`
- Introduces OAuth 2.0 Authorization Code Flow via `DiscordOAuthHandler`
- Handles authentication and token management

Testing:
- Unit tests mock Discord API responses
- Ensures deterministic and isolated testing

---

### 2. discord_service

This component exposes the Discord client functionality as a FastAPI service.

Structure:
- Located in `src/discord_service/main.py`
- Defines REST endpoints corresponding to client methods

Endpoints:
- `GET /health`
- `GET /auth/login`
- `GET /auth/callback`
- `GET /channels`
- `GET /channels/{channel_id}/messages`
- `POST /channels/{channel_id}/messages`

Responsibilities:
- Acts as a thin wrapper over `discord_client_impl`
- Translates HTTP requests into method calls
- Returns JSON responses

Deployment:
- Deployed on Google Cloud Run:
  - https://discord-service-122083288286.us-east4.run.app

---

### 3. discord_service_api_client

This component is an auto-generated Python client based on the OpenAPI specification of the deployed service.

Generation:
- Generated using `openapi-python-client`
- Source spec:
  - https://discord-service-122083288286.us-east4.run.app/openapi.json

Structure:
- Contains:
  - API endpoint wrappers (`api/default/...`)
  - Typed models (`models/...`)
  - Client configuration (`client.py`)

Features:
- Type-safe API calls
- Matches all service endpoints:
  - health
  - auth
  - channels
  - messages

Usage:
- Acts as the programmatic interface for interacting with the deployed service
- Used in integration and end-to-end tests

---

## Architecture

The overall system architecture is:
chat_client_api (interface)
↓
discord_client_impl (real Discord API)
↓
discord_service (FastAPI)
↓
OpenAPI spec (/openapi.json)
↓
discord_service_api_client (generated client)



Unlike a traditional adapter-based architecture, this design directly exposes the implementation through a service layer, and uses a generated client as the integration boundary.

---

## Design Decisions

### 1. Service-Oriented Architecture

Instead of directly coupling the client implementation with consumers, we introduce a FastAPI service layer.

Benefits:
- Enables remote access via HTTP
- Supports independent deployment
- Decouples implementation from usage

---

### 2. OpenAPI-Based Client Generation

We use OpenAPI to automatically generate a client.

Benefits:
- Eliminates manual client implementation
- Ensures consistency with service endpoints
- Provides type safety

---

### 3. OAuth 2.0 Integration

We implement OAuth 2.0 Authorization Code Flow.

Benefits:
- Secure authentication with Discord
- Industry-standard approach
- Required for accessing user-specific resources

---

### 4. Testing Strategy

We separate testing into multiple levels:

- Unit tests:
  - Mock Discord API responses
- Integration tests:
  - Use generated API client
- E2E tests:
  - Run against real deployed service

---

## Changes Summary

Main updates in this PR:

- DiscordClient now makes real API calls to Discord for get_channels, get_messages, send_message  
- Added DiscordOAuthHandler class for OAuth 2.0 flow  
- Added py.typed marker for mypy support  
- Updated unit tests with mocked API responses (28 tests, 100% coverage)  
- Updated E2E test to run against real Discord API with graceful skip  
- Fixed integration test to use monkeypatched credentials  
- Updated READMEs for both components  
- Added all 5 required environment variables  
- Deployed FastAPI service to Google Cloud Run (https://discord-service-122083288286.us-east4.run.app)  
- Created Dockerfile, .dockerignore, and cloudbuild.yaml for containerized deployment  
- Set up Cloud Build trigger — auto-deploys on every push to hw-2 from GitHub  
- Configured GCP project ospsd8-discord with IAM roles, Secret Manager, Artifact Registry  
- Environment variables stored securely via Cloud Run — not in source control  
- Generated discord_service_api_client using openapi-python-client from deployed service OpenAPI spec  
- Type-safe Python client for all endpoints: health, auth, channels, messages  

---

## Evidence / Validation
$ curl https://discord-service-122083288286.us-east4.run.app/health

{"status":"ok"}


- CircleCI Pipeline #67: lint and test passing  
- Cloud Build: auto-deploy from GitHub trigger working  
- OpenAPI spec:
  https://discord-service-122083288286.us-east4.run.app/openapi.json  

