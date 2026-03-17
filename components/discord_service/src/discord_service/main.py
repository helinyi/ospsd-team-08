"""The endpoints for the Discord service."""

import os
from typing import Annotated

import uvicorn
from chat_client_api.models import Channel, Message
from discord_client_impl.client import DiscordClient
from dotenv import load_dotenv
from fastapi import Body, FastAPI, HTTPException

load_dotenv()

app = FastAPI()


def get_client() -> DiscordClient:  # pragma: no cover
    """Create a DiscordClient instance."""
    return DiscordClient()


@app.get("/health")
def health() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok"}


@app.get("/channels")
def get_channels() -> list[Channel]:
    """Return the channels."""
    return get_client().get_channels()


def _get_channel_by_id(channel_id: str) -> Channel:
    """Resolve a string ID into a Channel object reference."""
    channels = get_client().get_channels()
    target = next((c for c in channels if c.id == channel_id), None)

    if not target:
        raise HTTPException(
            status_code=404,
            detail=f"Channel with ID {channel_id} not found in this guild."
        )
    return target


@app.post("/channels/{channel_id}/messages")
async def send_channel_message(
    channel_id: str, content: Annotated[str, Body(embed=True)]
) -> Message:
    """Send a message to a specific Discord channel.

    Args:
        channel_id: The ID of the Discord channel.
        content: The text of the message.

    """
    channel_obj = _get_channel_by_id(channel_id)

    try:
        return get_client().send_message(channel_obj, content)

    except RuntimeError as error:
        raise HTTPException(status_code=502, detail=f"Discord API error: {error}") from error


if __name__ == "__main__":
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", "8000"))

    uvicorn.run(app, host=host, port=port)
