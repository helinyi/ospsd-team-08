# Contributing Guide

Thank you for contributing to this project.

This repository follows a component-based architecture with clear separation between interface and implementation. Please read this guide before adding new features or providers.

---

## Project Structure

The project is organized into components:
```
components/
├── ai_client_api/              # Abstract AI client interface
├── openai_ai_client_impl/      # OpenAI implementation with tool calling
├── calendar_integration/       # Google Calendar cross-vertical integration
├── google_calendar_adapter/    # Google Calendar API adapter
├── discord_client_impl/        # Discord implementation + OAuth 2.0
├── discord_service/            # FastAPI microservice
├── discord_service_api_client/ # Auto-generated API client
└── chat_client_adapter/        # Service client adapter
```
Each component is independently packaged using the `src/` layout.

---

## Architectural Principles

When contributing, follow these rules:

### 1. Interface Purity

- `chat_client_api` is an external shared vertical API — do not modify it directly.
- No provider-specific types may appear in the interface.
- No SDK imports inside the interface component.
- The interface defines *what*, never *how*.

### 2. Implementation Isolation

- Implementation packages depend on `chat_client_api`.
- Implementations must inherit from `ChatClient`.
- All abstract methods must be fully implemented.
- No hardcoded credentials — use environment variables.

### 3. Dependency Injection

If adding a new provider:

- Register the implementation using `register_client()`
- Do not modify the interface package to support a specific provider.

---

## Adding a New Chat Provider

To add a new provider (e.g., `telegram_client_impl`):

1. Create a new component under `components/`
2. Use `src/` layout
3. Add a concrete class inheriting from `ChatClient`
4. Implement all 6 abstract methods
5. Register factory for dependency injection
6. Add a component README
7. Update documentation

## Adding a New AI Provider

To add a new AI provider (e.g., `claude_ai_client_impl`):

1. Create a new component under `components/`
2. Inherit from `AIClient` defined in `ai_client_api`
3. Implement `run(user_input, context)` with tool calling support
4. Wire tools to domain actions via `ChatClient`
5. Load credentials from environment variables

---

## Development Workflow

### Setup

```bash
uv sync --all-packages
```

### Run Tests
```bash
uv run pytest
```

### Lint and Type Check
```bash
uv run ruff check .
uv run mypy components/
```

### Run Documentation
```bash
uv run mkdocs serve
```