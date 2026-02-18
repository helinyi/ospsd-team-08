# Getting Started

## Prerequisites

- Python 3.10 or higher
- [uv](https://docs.astral.sh/uv/) package manager

---

## Installation

1. Clone the repository:

```bash
git clone <your-repository-url>
cd opssd-team-08
```

2. Install dependencies:

```bash
uv sync
```

---

## Running Tests

Run all tests:

```bash
uv run pytest
```

---

## Using the Chat Client

Import the implementation to register the client factory:

```python
import discord_client_impl
from chat_client_api import get_client

client = get_client()

channels = client.get_channels()
messages = client.get_messages("channel_id")

client.send_message("channel_id", "Hello!")
```

---

## Dependency Injection

This project uses a simple dependency injection pattern.

Concrete implementations (e.g., `discord_client_impl`) register a factory
that provides a `ChatClient` instance.

Users only need to import the implementation and call:

```python
import discord_client_impl
from chat_client_api import get_client

client = get_client()
```

If no implementation is imported, calling `get_client()` will raise a `RuntimeError`.

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
