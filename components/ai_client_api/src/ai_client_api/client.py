"""Abstract interface for AI client implementations."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


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
