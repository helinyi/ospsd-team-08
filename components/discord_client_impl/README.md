
# discord_client_impl/README.md

```markdown
# discord_client_impl

## Purpose

`discord_client_impl` provides a concrete implementation of the `ChatClient` interface for Discord.

This component implements the abstract contract defined in `chat_client_api` and makes real HTTP calls to the Discord API using bot token authentication and OAuth 2.0.


---

## Architecture Role

This component represents the **Implementation Component**.

It:

- Inherits from `ChatClient`
- Implements all abstract methods with real Discord API calls
- Handles bot token authentication and OAuth 2.0 flows
- Depends on `chat_client_api`
- Does not expose Discord SDK types through the interface

Users interact with the `ChatClient` interface, not directly with this implementation.

---

## Implementation Details

The main classes:
```python
class DiscordClient(ChatClient)
class DiscordAuthenticator
class DiscordOAuthHandler
```

### Methods
| Method | Description |
|---|---|
| `get_channels()` | Returns all text channels in the guild |
| `get_channel(channel_id)` | Returns a single channel by ID |
| `get_messages(channel_id, limit, cursor)` | Returns recent messages oldest first |
| `get_message(message_id)` | Returns a single message by opaque ID |
| `send_message(channel_id, text)` | Sends a message to a channel |
| `delete_message(message_id)` | Deletes a message by opaque ID |

### Message ID Format
`message_id` is encoded as `"channel_id:discord_message_id"` to satisfy the shared interface's single-string requirement.

---

## Required Environment Variables

| Variable | Description |
|---|---|
| `DISCORD_CLIENT_ID` | OAuth2 Client ID from Discord Developer Portal |
| `DISCORD_CLIENT_SECRET` | OAuth2 Client Secret from Discord Developer Portal |
| `DISCORD_BOT_TOKEN` | Bot token from Discord Developer Portal |
| `DISCORD_GUILD_ID` | ID of the Discord server to operate on |
| `DISCORD_REDIRECT_URI` | OAuth2 redirect URI (default: `http://localhost:8000/auth/callback`) |

---

##  Dependencies

This component depends on:

- `chat_client_api`
- `requests`
- Python standard library