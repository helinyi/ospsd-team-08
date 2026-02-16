"""Main entry point for the Chat Client application."""

from __future__ import annotations

from chat_client_api import get_client


def main() -> None:
    """Run the chat client demo against the Discord API."""
    client = get_client()

    print("Channels: ")
    channels = client.get_channels()
    for channel in channels:
        print(f"  #{channel.name} -- {channel.topic or 'no topic'}")

    if channels:
        first = channels[0]
        print(f"\n Recent messages in #{first.name} ---")
        messages = client.get_messages(first.id, limit=5)
        for msg in messages:
            print(f"  [{msg.timestamp:%Y-%m-%d %H:%M}] {msg.sender}: {msg.content}")


if __name__ == "__main__":
    main()
