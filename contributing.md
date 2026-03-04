# Contributing Guide

Thank you for contributing to this project.

This repository follows a component-based architecture with clear separation between interface and implementation. Please read this guide before adding new features or providers.

---

## Project Structure

The project is organized into components:
components/
chat_client_api/ # Abstract interface
discord_client_impl/ # Concrete implementation
docs/
mkdocs.yml



Each component is independently packaged using the `src/` layout.

---

## Architectural Principles

When contributing, follow these rules:

### 1. Interface Purity

- `chat_client_api` must NOT depend on any implementation package.
- No provider-specific types may appear in the interface.
- No SDK imports inside the interface component.
- The interface defines *what*, never *how*.

### 2. Implementation Isolation

- Implementation packages depend on `chat_client_api`.
- Implementations must inherit from `ChatClient`.
- All abstract methods must be fully implemented.
- No hardcoded credentials.

### 3. Dependency Injection

If adding a new provider:

- Register the implementation using `register_client_factory()`
- Do not modify the interface package to support a specific provider.

---

## Adding a New Provider

To add a new provider (e.g., `telegram_client_impl`):

1. Create a new component under `components/`
2. Use `src/` layout
3. Add a concrete class inheriting from `ChatClient`
4. Implement all abstract methods
5. (Optional) Register factory for dependency injection
6. Add a component README
7. Update documentation

---

## Development Workflow

### Setup

```bash
uv sync
```

### Run Tests
```bash
uv run pytest
```

### Run Documentation
```bash
uv run mkdocs serve
```

