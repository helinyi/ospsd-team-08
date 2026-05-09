"""The endpoints for the Discord service."""

from __future__ import annotations

import os
import secrets as _secrets  # pragma: no cover
from datetime import UTC, datetime
from typing import Annotated

import discord_client_impl  # noqa: F401
import google_calendar_adapter  # noqa: F401
import requests
import uvicorn
from ai_client_api import ToolLoopExhaustedError
from ai_client_api import get_client as get_ai_client
from calendar_client_api.client import Client as CalendarClient  # noqa: TC002
from calendar_integration.service import (
    get_events_message,
    get_tomorrows_events_message,
)
from chat_client_api import Channel, Message
from chat_client_api import get_client as get_chat_client
from chat_client_api.client import ChatClient  # noqa: TC002
from discord_client_impl.auth import DiscordOAuthHandler
from dotenv import load_dotenv
from fastapi import Body, Depends, FastAPI, HTTPException, Query, Request
from fastapi.responses import RedirectResponse
from google_calendar_adapter import get_calendar_client as get_connected_calendar_client
from prometheus_fastapi_instrumentator import Instrumentator
from starlette.middleware.sessions import SessionMiddleware

load_dotenv()

app = FastAPI()
Instrumentator().instrument(app).expose(app)    # pragma: no cover


secret_key = os.environ.get("SESSION_SECRET_KEY")
if not secret_key:
    secret_key = _secrets.token_urlsafe(32)  # pragma: no cover

app.add_middleware(SessionMiddleware, secret_key=secret_key)


def get_client() -> ChatClient:  # pragma: no cover
    """Create a ChatClient instance via dependency injection."""
    return get_chat_client()


def get_oauth_handler() -> DiscordOAuthHandler:
    """Dependency for OAuth flow management."""
    return DiscordOAuthHandler.from_env()


def get_calendar_client() -> CalendarClient:  # pragma: no cover
    """Create a CalendarClient instance via dependency injection."""
    try:
        return get_connected_calendar_client()
    except (RuntimeError, FileNotFoundError) as error:
        raise HTTPException(status_code=503, detail=str(error)) from error


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
    request: Request,
    oauth: Annotated[DiscordOAuthHandler, Depends(get_oauth_handler)],
) -> dict[str, str]:
    """Exchanges the authorization code for an access token."""
    try:
        token = oauth.exchange_code(code)
    except RuntimeError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    request.session["access_token"] = token
    return {"message": "Authentication successful"}


@app.get("/users/me")
def get_current_user(request: Request) -> dict[str, str]:
    """Return the currently authenticated Discord user.

    Requires the user to have logged in via /auth/login first.

    Raises:
        HTTPException: If the user is not authenticated or the API call fails.

    """
    access_token = request.session.get("access_token")
    if not access_token:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated. Visit /auth/login first.",
        )
    try:
        response = requests.get(
            "https://discord.com/api/v10/users/@me",
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=10,
        )
    except requests.RequestException as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    if not response.ok:
        raise HTTPException(
            status_code=response.status_code,
            detail="Failed to fetch user info from Discord.",
        )
    data: dict[str, str] = response.json()
    return {
        "id": data.get("id", ""),
        "username": data.get("username", ""),
        "discriminator": data.get("discriminator", ""),
    }


@app.get("/channels")
def get_channels(
    client: Annotated[ChatClient, Depends(get_client)],
) -> list[Channel]:
    """Return the channels."""
    return client.get_channels()


def _get_channel_by_id(channel_id: str, client: ChatClient) -> Channel:
    """Resolve a string ID into a Channel object reference."""
    channels = client.get_channels()
    target = next((c for c in channels if c.channel_id == channel_id), None)

    if not target:
        raise HTTPException(
            status_code=404,
            detail=f"Channel with ID {channel_id} not found in this guild.",
        )
    return target


@app.post("/channels/{channel_id}/messages")
async def send_channel_message(
    client: Annotated[ChatClient, Depends(get_client)],
    channel_id: str,
    content: Annotated[str, Body(embed=True)],
) -> Message:
    """Send a message to a specific Discord channel.

    Args:
        client: The DiscordClient instance to use for API calls.
        channel_id: The ID of the Discord channel.
        content: The text of the message.

    """
    _get_channel_by_id(channel_id, client)

    try:
        return client.send_message(channel_id, content)

    except RuntimeError as error:
        raise HTTPException(
            status_code=502, detail=f"Discord API error: {error}"
        ) from error


@app.get("/channels/{channel_id}/messages")
def get_channel_messages(
    channel_id: str,
    client: Annotated[ChatClient, Depends(get_client)],
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
    _get_channel_by_id(channel_id, client)

    try:
        return client.get_messages(channel_id, limit=limit)

    except RuntimeError as error:
        raise HTTPException(
            status_code=502, detail=f"Discord API error: {error}"
        ) from error

@app.get("/calendar/tomorrow")
def get_tomorrows_events(
        calendar_client: Annotated[CalendarClient, Depends(get_calendar_client)],
) -> dict[str, str]:
    """Return tomorrow's calendar events as a formatted chat message."""
    try:
        message = get_tomorrows_events_message(calendar_client, datetime.now(UTC))
    except RuntimeError as error:
        raise HTTPException(status_code=502, detail=str(error)) from error

    return {"message": message}

@app.get("/calendar/events")
def get_calendar_events(
        start_time: datetime,
        end_time: datetime,
        calendar_client: Annotated[CalendarClient, Depends(get_calendar_client)],
) -> dict[str, str]:
    """Return calendar events for a given time range."""
    message = get_events_message(calendar_client, start_time, end_time)
    return {"message": message}


@app.post("/ai/chat")
def ai_chat(
    user_input: Annotated[str, Body(embed=True)],
) -> dict[str, str]:
    """AI chat endpoint that uses the registered AI client."""
    try:
        ai_client = get_ai_client()
        response = ai_client.run(user_input)
    except ToolLoopExhaustedError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error)) from error
    else:
        return {"response": response}


if __name__ == "__main__":
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", "8000"))

    uvicorn.run(app, host=host, port=port)
