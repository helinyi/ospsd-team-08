"""Abstract interface for AI client implementations."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Callable


class ToolLoopExhaustedError(Exception):
    """Raised when the AI tool-calling loop exhausts its maximum iterations."""


class AIClient(ABC):
    """Abstract contract for an AI client."""

    @abstractmethod
    def run(
        self,
        user_input: str,
        context: dict[str, Any] | None = None,
    ) -> str:
        """Process user input and return a response."""


_factory: Callable[[], AIClient] | None = None


def register_client(factory: Callable[[], AIClient]) -> None:
    """Register a concrete AIClient factory."""
    global _factory  # noqa: PLW0603
    _factory = factory


def get_client() -> AIClient:
    """Return an AIClient instance from the registered factory."""
    if _factory is None:
        msg = "No AI client implementation registered."
        raise RuntimeError(msg)
    return _factory()
