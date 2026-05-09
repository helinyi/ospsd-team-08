# API Reference

## ChatClient Interface

### get_channels() -> list[Channel]
Retrieve all accessible channels.

### get_channel(channel_id: str) -> Channel
Retrieve a single channel by ID.

### get_messages(channel_id: str, limit: int = 10, cursor: str | None = None) -> list[Message]
Retrieve recent messages from a channel, oldest first.

### get_message(message_id: str) -> Message
Retrieve a single message by its opaque ID.

### send_message(channel_id: str, text: str) -> Message
Send a message to a channel.

### delete_message(message_id: str) -> None
Delete a message by its opaque ID.

## Factory / Dependency Injection

### register_client(factory: Callable[[], ChatClient]) -> None
Register a concrete `ChatClient` factory.

### get_client() -> ChatClient
Return a `ChatClient` instance from the registered factory. Raises `RuntimeError` if no implementation is registered.

## Data Models

### Channel
- channel_id (str): Channel identifier
- name (str): Channel name
- is_private (bool | None): Whether the channel is private
- channel_type (str | None): Channel type

### Message
- message_id (str): Opaque message identifier encoded as `"channel_id:discord_message_id"`
- channel (str): Channel ID the message belongs to
- text (str): Message content
- sender (str): Sender identifier
- timestamp (datetime): Timezone-aware datetime

## AI Client Interface

### AIClient.run(user_input: str, context: dict | None = None) -> str
Process a natural language request and return a response. Supports tool calling for domain actions.

## Custom Exceptions

- `ChatError` — base exception
- `ChannelNotFoundError` — raised when a channel is not found
- `MessageNotFoundError` — raised when a message is not found

## Calendar Integration

### GET /calendar/tomorrow
Returns tomorrow's Google Calendar events formatted as a chat message.

**Response:**
```json
{"message": "- Team Standup | 09:00:00+00:00 to 09:30:00+00:00"}
```

**Errors:**
- `503` — Google Calendar credentials not configured

### GET /calendar/events?start_time=...&end_time=...
Returns calendar events for a given time range.

**Parameters:**
- `start_time` (datetime): Start of time range (ISO format)
- `end_time` (datetime): End of time range (ISO format)

**Response:**
```json
{"message": "- OSPSD Class | 14:00:00+00:00 to 15:30:00+00:00"}
```

## CalendarClient Interface (cross-vertical)

The calendar integration depends on the shared `calendar-client-api` from Team 5:

### get_events(start_time: datetime, end_time: datetime) -> Iterable[Event]
Fetch calendar events within a time range.

### Event Model
- `id` (str): Event identifier
- `title` (str): Event title
- `start_time` (datetime): Event start time
- `end_time` (datetime): Event end time
- `location` (str | None): Event location
- `description` (str | None): Event description