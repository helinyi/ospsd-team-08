"""OpenAI-backed AI client implementation with tool calling."""

from __future__ import annotations

import json
import os
from typing import TYPE_CHECKING, Any, cast

from ai_client_api import AIClient, ToolLoopExhaustedError
from chat_client_api import get_client
from openai import OpenAI

from openai_ai_client_impl.tools import build_openai_tools, get_tool_handlers

if TYPE_CHECKING:
    from collections.abc import Callable

    from chat_client_api import ChatClient
    from openai.types.chat.chat_completion_message import ChatCompletionMessage


class OpenAIAIClient(AIClient):
    """OpenAI-backed AI client with tool calling over the shared chat API."""

    MAX_TOOL_ITERATIONS = 5  # Maximum number of tool-calling iterations

    def __init__(
        self,
        chat_client: ChatClient | None = None,
        model: str = "gpt-4o-mini",
        extra_tool_handlers: dict[str, Callable[..., str]] | None = None,
    ) -> None:
        """Initialize the AI client.

        Args:
            chat_client: Optional chat client implementation. If omitted,
                the registered shared chat client is used.
            model: OpenAI model name.
            extra_tool_handlers: Optional additional tool handlers for
                cross-vertical actions (e.g. calendar tools).

        Raises:
            ValueError: If OPENAI_API_KEY is not set.

        """
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            msg = "OPENAI_API_KEY is not set."
            raise ValueError(msg)

        self._client = OpenAI(api_key=api_key)
        self._chat_client = chat_client if chat_client is not None else get_client()
        self._model = model
        self._tools = build_openai_tools()
        self._tool_handlers = {
            **get_tool_handlers(self._chat_client),
            **(extra_tool_handlers or {}),
        }

    def run(
        self,
        user_input: str,
        context: dict[str, Any] | None = None,
    ) -> str:
        """Process user input and return a response.

        Args:
            user_input: The user's natural-language request.
            context: Optional extra context for the model.

        Returns:
            The assistant's final response.

        """
        messages: list[dict[str, Any]] = [
            {
                "role": "system",
                "content": (
                    "You are an assistant for a chat application. "
                    "You can inspect channels, read messages, and send messages "
                    "by calling tools. "
                    "If the user asks for channel or message information, prefer "
                    "using tools instead of guessing. "
                    "Do not invent channel IDs, message IDs, or message contents. "
                    "When a tool result is returned, use it to answer clearly."
                ),
            }
        ]

        if context is not None:
            messages.append(
                {
                    "role": "system",
                    "content": f"Extra context: {self._safe_json_dump(context)}",
                }
            )

        messages.append({"role": "user", "content": user_input})

        for _ in range(self.MAX_TOOL_ITERATIONS):
            response = self._client.chat.completions.create(
                model=self._model,
                messages=cast("Any", messages),
                tools=cast("Any", self._tools),
                tool_choice="auto",
            )

            assistant_message = response.choices[0].message
            messages.append(self._assistant_message_to_dict(assistant_message))

            if not assistant_message.tool_calls:
                return assistant_message.content or ""

            for tool_call in assistant_message.tool_calls:
                function_obj = getattr(tool_call, "function", None)
                if function_obj is None:
                    continue

                tool_result = self._execute_tool_call(
                    tool_name=function_obj.name,
                    raw_arguments=function_obj.arguments,
                )

                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": tool_result,
                    }
                )

        msg = f"AI tool-calling loop exhausted after {self.MAX_TOOL_ITERATIONS} iterations."
        raise ToolLoopExhaustedError(msg)

    def _execute_tool_call(self, tool_name: str, raw_arguments: str | None) -> str:
        """Execute a single tool call and return its serialized result.

        Args:
            tool_name: Name of the requested tool.
            raw_arguments: JSON-encoded tool arguments from the model.

        Returns:
            A JSON string containing the tool output or an error payload.

        """
        if tool_name not in self._tool_handlers:
            return json.dumps({"error": f"Unknown tool: {tool_name}"})

        try:
            parsed_arguments = self._parse_tool_arguments(raw_arguments)
        except (TypeError, ValueError, json.JSONDecodeError) as exc:
            return json.dumps({"error": str(exc)})

        try:
            return self._tool_handlers[tool_name](**parsed_arguments)
        except Exception as exc:  # noqa: BLE001
            return json.dumps({"error": str(exc)})

    @staticmethod
    def _parse_tool_arguments(raw_arguments: str | None) -> dict[str, Any]:
        """Parse tool arguments from the model.

        Args:
            raw_arguments: JSON string of arguments.

        Returns:
            Parsed arguments dictionary.

        Raises:
            TypeError: If arguments do not decode to a JSON object.
            json.JSONDecodeError: If JSON parsing fails.

        """
        if not raw_arguments:
            return {}

        parsed = json.loads(raw_arguments)
        if not isinstance(parsed, dict):
            msg = "Tool arguments must decode to a JSON object."
            raise TypeError(msg)
        return parsed

    @staticmethod
    def _assistant_message_to_dict(
        assistant_message: ChatCompletionMessage,
    ) -> dict[str, Any]:
        """Convert an OpenAI assistant message into a chat-completions message dict."""
        message_dict: dict[str, Any] = {"role": "assistant"}

        if assistant_message.content is not None:
            message_dict["content"] = assistant_message.content

        if assistant_message.tool_calls:
            serialized_tool_calls: list[dict[str, Any]] = []

            for tool_call in assistant_message.tool_calls:
                function_obj = getattr(tool_call, "function", None)
                if function_obj is None:
                    continue

                serialized_tool_calls.append(
                    {
                        "id": tool_call.id,
                        "type": tool_call.type,
                        "function": {
                            "name": function_obj.name,
                            "arguments": function_obj.arguments,
                        },
                    }
                )

            message_dict["tool_calls"] = serialized_tool_calls

        return message_dict

    @staticmethod
    def _safe_json_dump(value: object) -> str:
        """Serialize a value to JSON safely for prompt context."""
        try:
            return json.dumps(value)
        except TypeError:
            return json.dumps(str(value))
