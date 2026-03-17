import os
from fastapi import FastAPI
import uvicorn

from chat_client_api.models import Channel
from discord_client_impl.client import DiscordClient


app = FastAPI()
client = DiscordClient()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/channels")
def get_channels() -> list[Channel]:
    return client.get_channels()


if __name__ == "__main__":
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", "8000"))

    uvicorn.run(app, host=host, port=port)
