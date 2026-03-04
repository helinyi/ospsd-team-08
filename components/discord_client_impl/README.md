
# discord_client_impl/README.md

```markdown
# discord_client_impl

## Purpose

`discord_client_impl` provides a concrete implementation of the `ChatClient` interface for Discord.

This component implements the abstract contract defined in `chat_client_api`.

For HW1, this implementation is a minimal in-memory stub that demonstrates interface compliance.

---

## Architecture Role

This component represents the **Implementation Component**.

It:

- Inherits from `ChatClient`
- Implements all abstract methods
- Depends on `chat_client_api`
- Does not expose Discord SDK types through the interface

Users interact with the `ChatClient` interface, not directly with this implementation.

---

## Implementation Details

The main class:

```python
class DiscordClient(ChatClient)
```


##  Dependencies

This component depends on:

chat_client_api

Python standard library