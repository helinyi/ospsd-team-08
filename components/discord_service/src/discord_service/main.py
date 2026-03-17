"""The endpoints for the Discord service."""

import os

import uvicorn
from chat_client_api.models import Channel
from discord_client_impl.client import DiscordClient
from fastapi import FastAPI

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
    return client.get_channels()


if __name__ == "__main__":
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", "8000"))

    uvicorn.run(app, host=host, port=port)
