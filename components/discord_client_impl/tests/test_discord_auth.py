"""Unit tests for DiscordAuthenticator."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from discord_client_impl.auth import DiscordAuthenticator


def test_from_env_raises_when_token_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    """Raises RuntimeError when DISCORD_BOT_TOKEN is not set."""
    monkeypatch.delenv("DISCORD_BOT_TOKEN", raising=False)
    with pytest.raises(RuntimeError, match="DISCORD_BOT_TOKEN"):
        DiscordAuthenticator.from_env()


def test_from_env_succeeds_with_token(monkeypatch: pytest.MonkeyPatch) -> None:
    """Returns an authenticator when the env var is set."""
    monkeypatch.setenv("DISCORD_BOT_TOKEN", "test-token-123")
    auth = DiscordAuthenticator.from_env()
    assert auth is not None


def test_get_headers_returns_correct_format(monkeypatch: pytest.MonkeyPatch) -> None:
    """Authorization header uses the Bot scheme with the token."""
    monkeypatch.setenv("DISCORD_BOT_TOKEN", "my-secret-token")
    auth = DiscordAuthenticator.from_env()
    headers = auth.get_headers()
    assert headers["Authorization"] == "Bot my-secret-token"
    assert headers["Content-Type"] == "application/json"


def test_validate_raises_on_401() -> None:
    """Raises RuntimeError when Discord returns 401 Unauthorized."""
    auth = DiscordAuthenticator(token="bad-token")  # noqa: S106
    mock_response = MagicMock()
    mock_response.status_code = 401
    mock_response.ok = False
    with (
        patch("discord_client_impl.auth.requests.get", return_value=mock_response),
        pytest.raises(RuntimeError, match="401"),
    ):
        auth.validate()


def test_validate_raises_on_other_error() -> None:
    """Raises RuntimeError when Discord returns a non-200, non-401 status."""
    auth = DiscordAuthenticator(token="some-token")  # noqa: S106
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.ok = False
    with (
        patch("discord_client_impl.auth.requests.get", return_value=mock_response),
        pytest.raises(RuntimeError, match="500"),
    ):
        auth.validate()


def test_validate_succeeds() -> None:
    """Does not raise when Discord returns 200 OK."""
    auth = DiscordAuthenticator(token="valid-token")  # noqa: S106
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.ok = True
    with patch("discord_client_impl.auth.requests.get", return_value=mock_response):
        auth.validate()  # Should not raise
