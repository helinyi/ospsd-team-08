from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class AIClient(ABC):
    """Abstract contract for an AI client."""

    @abstractmethod
    def run(
        self,
        user_input: str,
        context: dict[str, Any] | None = None,
    ) -> str:
        """Process user input and return a response."""