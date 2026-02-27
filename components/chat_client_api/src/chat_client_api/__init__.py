"""Chat Client API — Abstract interface for chat clients."""

from __future__ import annotations

from typing import TYPE_CHECKING

from chat_client_api.client import ChatClient as ChatClient  # noqa: TC001
from chat_client_api.models import Channel as Channel
from chat_client_api.models import Message as Message

if TYPE_CHECKING:
    from collections.abc import Callable

_client_factory: Callable[[], ChatClient] | None = None


def _default_factory() -> ChatClient:
    """Raise an error when no implementation has been registered."""
    msg = "No ChatClient implementation registered. Import an implementation package (e.g., discord_client_impl) to inject one."
    raise RuntimeError(msg)


_client_factory = _default_factory


def get_client() -> ChatClient:
    """Return a ChatClient instance from the registered factory.

    Raises:
        RuntimeError: If no implementation has been registered.

    """
    if _client_factory is None:
        msg = "No ChatClient implementation registered."
        raise RuntimeError(msg)
    return _client_factory()


def register_client_factory(factory: Callable[[], ChatClient]) -> None:
    """Register a factory function that creates ChatClient instances.

    Called by implementation packages to inject themselves.
    """
    global _client_factory  # noqa: PLW0603
    _client_factory = factory
