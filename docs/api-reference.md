# API Reference

## ChatClient Interface

### get_channels() -> list[Channel]
Retrieve all accessible channels.

### get_messages(channel_id: str, limit: int = 10) -> list[Message]
Retrieve recent messages from a channel.

- channel_id: Target channel identifier
- limit: Maximum number of messages to return

### send_message(channel_id: str, content: str) -> Message
Send a message to a channel.

- channel_id: Target channel identifier
- content: Message content to send

## Factory / Dependency Injection

### register_client_factory(factory: Callable[[], ChatClient]) -> None
Register a concrete `ChatClient` factory (called by an implementation package).

### get_client() -> ChatClient
Return a `ChatClient` instance from the registered factory.

Raises `RuntimeError` if no implementation is registered.

## Data Models

### Channel
- id (str): Channel identifier
- name (str): Channel name
- topic (str): Channel topic (optional)

### Message
- id (str): Message identifier
- channel_id (str): Channel identifier
- sender (str): Sender identifier/name
- content (str): Message content
- timestamp (datetime): Message timestamp
