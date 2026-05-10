# HW3 Plan of Action — Team 8 (Discord)

## Shared Vertical API Alignment

### What Changed

Our existing codebase used a custom `chat_client_api` package with the following interface:
- `get_channels() -> list[Channel]`
- `get_messages(channel: Channel, limit: int) -> list[Message]`
- `send_message(channel: Channel, content: str) -> Message`

The shared vertical API agreed upon by Teams 4 (Telegram), 8 (Discord), and 9 (Slack) defines:
- `get_channels() -> list[Channel]`
- `get_channel(channel_id: str) -> Channel`
- `get_messages(channel_id: str, limit: int, cursor: str | None) -> list[Message]`
- `get_message(message_id: str) -> Message`
- `send_message(channel_id: str, text: str) -> Message`
- `delete_message(message_id: str) -> None`

### How We Adapted

1. **Replaced local `chat_client_api`** with the shared vertical API from the shared GitHub repository as a `uv` git dependency
2. **Updated `discord_client_impl`** to implement all 6 methods of the new shared interface using real Discord API calls
3. **Updated model field names** — `Channel.id` → `Channel.channel_id`, `Message.id` → `Message.message_id`, `Message.content` → `Message.text`, `Message.timestamp` from `datetime` to `str`
4. **Updated method signatures** — all methods now accept `channel_id: str` instead of `Channel` objects
5. **Added 3 new methods** — `get_channel`, `get_message`, and `delete_message`
6. **Updated all tests** across `discord_client_impl`, `discord_service`, and `chat_client_adapter`

### Message ID Format

Discord's API requires both a channel ID and message ID to fetch or delete a message. We encode the opaque `message_id` as `"channel_id:message_id"` to satisfy the shared interface's single-string requirement.

### Cursor Pagination

The shared API includes an optional `cursor` parameter in `get_messages`. Discord supports cursor-based pagination via the `before` parameter. We map `cursor` to `before` when provided.