# chat_client_api

## Purpose

`chat_client_api` defines the abstract interface (contract) for chat clients.

This component specifies *what* a chat client must do, without specifying *how* it is implemented. It ensures that different providers (e.g., Discord, Telegram, etc.) can implement the same interface consistently.

This package contains:
- The abstract `ChatClient` base class
- Data models (`Channel`, `Message`)
- A factory registration mechanism for dependency injection

---

## Architecture Role

This component represents the **Interface Component** in the project architecture.

It:

- Defines the abstract contract using Python ABCs
- Exposes provider-agnostic data models
- Contains no implementation-specific logic
- Has zero dependencies on implementation packages

Other components (e.g., `discord_client_impl`) must depend on this package, but this package must not depend on them.

---

## Public API

### Abstract Interface

```python
class ChatClient(ABC):
    def get_channels(self) -> list[Channel]: ...
    def get_messages(self, channel: Channel, limit: int = 10) -> list[Message]: ...
    def send_message(self, channel: Channel, content: str) -> Message: ...
```

---

## Dependencies

This component:

Uses only Python standard library modules

Has no external SDK or provider dependencies

Has no dependency on implementation packages