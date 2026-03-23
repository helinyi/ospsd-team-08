"""The endpoints for the Discord service."""

import os
from typing import Annotated

import uvicorn
from chat_client_api.models import Channel, Message
from discord_client_impl.auth import DiscordOAuthHandler
from discord_client_impl.client import DiscordClient
from dotenv import load_dotenv
from fastapi import Body, Depends, FastAPI, HTTPException, Query
from fastapi.responses import RedirectResponse

load_dotenv()

app = FastAPI()


def get_client() -> DiscordClient:  # pragma: no cover
    """Create a DiscordClient instance."""
    return DiscordClient()


def get_oauth_handler() -> DiscordOAuthHandler:
    """Dependency for OAuth flow management."""
    return DiscordOAuthHandler.from_env()


@app.get("/health")
def health() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok"}


@app.get("/auth/login")
def login(
    oauth: Annotated[DiscordOAuthHandler, Depends(get_oauth_handler)],
) -> RedirectResponse:
    """Redirects the user to Discord's authorization page."""
    return RedirectResponse(oauth.get_authorization_url())


@app.get("/auth/callback")
def auth_callback(
    code: str,
    oauth: Annotated[DiscordOAuthHandler, Depends(get_oauth_handler)],
) -> dict[str, str]:
    """Exchanges the authorization code for an access token."""
    try:
        token = oauth.exchange_code(code)
    except RuntimeError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    else:
        return {"access_token": token, "token_type": "Bearer"}


@app.get("/channels")
def get_channels(
    client: Annotated[DiscordClient, Depends(get_client)],
) -> list[Channel]:
    """Return the channels."""
    return client.get_channels()


def _get_channel_by_id(
    channel_id: str, client: Annotated[DiscordClient, Depends(get_client)]
) -> Channel:
    """Resolve a string ID into a Channel object reference."""
    channels = client.get_channels()
    target = next((c for c in channels if c.id == channel_id), None)

    if not target:
        raise HTTPException(
            status_code=404,
            detail=f"Channel with ID {channel_id} not found in this guild."
        )
    return target


@app.post("/channels/{channel_id}/messages")
async def send_channel_message(
    client: Annotated[DiscordClient, Depends(get_client)],
    channel_id: str,
    content: Annotated[str, Body(embed=True)],
) -> Message:
    """Send a message to a specific Discord channel.

    Args:
        client: The DiscordClient instance to use for API calls.
        channel_id: The ID of the Discord channel.
        content: The text of the message.

    """
    channel_obj = _get_channel_by_id(channel_id, client)

    try:
        return client.send_message(channel_obj, content)

    except RuntimeError as error:
        raise HTTPException(status_code=502, detail=f"Discord API error: {error}") from error


@app.get("/channels/{channel_id}/messages")
def get_channel_messages(
    channel_id: str,
    client: Annotated[DiscordClient, Depends(get_client)],
    limit: Annotated[
        int, Query(description="Number of messages to fetch", gt=0, le=100)
    ] = 10,
) -> list[Message]:
    """Retrieve recent messages from a specific channel.

    Args:
        channel_id: The ID of the Discord channel.
        client: The DiscordClient instance to use for API calls.
        limit: The maximum number of messages to return (default 10, max 100).

    """
    channel_obj = _get_channel_by_id(channel_id, client)

    try:
        return client.get_messages(channel_obj, limit=limit)

    except RuntimeError as error:
        raise HTTPException(
            status_code=502, detail=f"Discord API error: {error}"
        ) from error


if __name__ == "__main__":
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", "8000"))

    uvicorn.run(app, host=host, port=port)
